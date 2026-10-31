import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.core.database import get_db, _db_connected
from backend.models.conversation import Conversation
from backend.models.message import Message
from backend.schemas.chat import (
    ChatRequest, ChatResponse, ConversationSummary,
    ConversationDetail, MessageDetail, Citation
)
from backend.services.ai_service import ai_service
from backend.services.rag_service import rag_service
from backend.services.viewer_service import viewer_service
from backend.services.intent_service import intent_service
from backend.services.multimodal_service import multimodal_service
from backend.core.logging import logger

router = APIRouter(prefix="/api", tags=["Chat & Conversations"])

# In-memory session fallback store when MySQL is unconfigured/connecting
_fallback_conversations = {}

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Primary conversational endpoint for F.R.I.D.A.Y.
    Executes Chrome & Spotify directives, RAG retrieval, 3D viewer commands, and multimodal AI.
    """
    conv_id = request.conversation_id or str(uuid.uuid4())
    user_prompt = request.prompt.strip()

    # Step 1: Detect Chrome & Spotify voice/automation directives
    intent_result = intent_service.detect_and_execute(user_prompt)
    if intent_result.is_handled:
        ai_reply = intent_result.response_message
        citations: List[Citation] = []
        viewer_actions = None
        db: Optional[Session] = None
        if _db_connected:
            try:
                from backend.core.database import _SessionLocal
                if _SessionLocal:
                    db = _SessionLocal()
                    existing_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                    if not existing_conv:
                        title = user_prompt[:35] + ("..." if len(user_prompt) > 35 else "")
                        existing_conv = Conversation(id=conv_id, title=title)
                        db.add(existing_conv)
                        db.commit()
            except Exception as e:
                logger.warning(f"Database error in chat: {e}")
                if db:
                    db.rollback()
        else:
            if conv_id not in _fallback_conversations:
                _fallback_conversations[conv_id] = {
                    "id": conv_id,
                    "title": user_prompt[:35] + ("..." if len(user_prompt) > 35 else ""),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "messages": []
                }

        msg_id = str(uuid.uuid4())
        # Save to database or fallback
        if db and _db_connected:
            try:
                user_msg = Message(
                    id=str(uuid.uuid4()),
                    conversation_id=conv_id,
                    role="user",
                    content=user_prompt,
                    modality=request.modality
                )
                asst_msg = Message(
                    id=msg_id,
                    conversation_id=conv_id,
                    role="assistant",
                    content=ai_reply,
                    modality="text"
                )
                db.add(user_msg)
                db.add(asst_msg)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to save intent message: {e}")
                db.rollback()
            finally:
                db.close()
        else:
            conv_record = _fallback_conversations.get(conv_id)
            if conv_record:
                conv_record["updated_at"] = datetime.now(timezone.utc).isoformat()
                conv_record["messages"].append({
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": user_prompt,
                    "modality": request.modality,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
                conv_record["messages"].append({
                    "id": msg_id,
                    "role": "assistant",
                    "content": ai_reply,
                    "modality": "text",
                    "citations": [],
                    "metadata_json": None,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })

        return ChatResponse(
            conversation_id=conv_id,
            message_id=msg_id,
            response=ai_reply,
            reply=ai_reply,
            citations=[],
            modality="text",
            status="success",
            viewer_actions=None
        )

    # Step 2: Detect 3D viewer actions
    viewer_actions = None
    is_3d_cmd, parsed_actions, _ = viewer_service.parse_command(user_prompt)
    if is_3d_cmd:
        viewer_actions = parsed_actions


    # Step 2: Retrieve RAG knowledge if requested
    grounded_context = ""
    citations: List[Citation] = []
    if request.use_rag:
        try:
            ctx_text, raw_citations = rag_service.build_grounded_context(user_prompt, top_k=3)
            grounded_context = ctx_text
            citations = [Citation(**c) for c in raw_citations]
        except Exception as e:
            logger.warning(f"RAG retrieval encountered an issue: {e}")

    # Step 3: Fetch history if available
    conversation_history = []
    db: Optional[Session] = None
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                db = _SessionLocal()
                existing_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
                if not existing_conv:
                    title = user_prompt[:35] + ("..." if len(user_prompt) > 35 else "")
                    existing_conv = Conversation(id=conv_id, title=title)
                    db.add(existing_conv)
                    db.commit()
                else:
                    for m in existing_conv.messages[-6:]:
                        conversation_history.append({"role": m.role, "content": m.content})
        except Exception as e:
            logger.warning(f"Database read issue in chat: {e}")
            if db:
                db.rollback()
    else:
        # Use fallback memory
        if conv_id not in _fallback_conversations:
            _fallback_conversations[conv_id] = {
                "id": conv_id,
                "title": user_prompt[:35] + ("..." if len(user_prompt) > 35 else ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "messages": []
            }
        recent = _fallback_conversations[conv_id]["messages"][-6:]
        conversation_history = [{"role": m["role"], "content": m["content"]} for m in recent]

    # Step 4: Generate Assistant Response (Multimodal Vision or LLM)
    if request.image_base64:
        analysis_result = multimodal_service.analyze_image(
            prompt=user_prompt,
            image_base64=request.image_base64,
            task_type=request.task_type or "general"
        )
        ai_reply = analysis_result.get("analysis", "Visual analysis complete, Boss.")
    else:
        ai_reply = ai_service.generate_chat_response(
            prompt=user_prompt,
            conversation_history=conversation_history,
            context_text=grounded_context,
            support_mode=request.support_mode
        )

    # Intercept and execute any LLM action directives
    import re
    from backend.integrations.desktop_control import desktop_control
    from backend.integrations.spotify import spotify_integration

    from backend.integrations.music_player import music_player

    m_act_site = re.search(r"\[ACTION:\s*OPEN_WEBSITE:\s*(.+?)\]", ai_reply, re.IGNORECASE)
    if m_act_site:
        target_site = m_act_site.group(1).strip()
        desktop_control.open_website(target_site)
        ai_reply = re.sub(r"\[ACTION:\s*OPEN_WEBSITE:\s*.+?\]", "", ai_reply, flags=re.IGNORECASE).strip()

    m_act_chrome = re.search(r"\[ACTION:\s*OPEN_CHROME\]", ai_reply, re.IGNORECASE)
    if m_act_chrome:
        desktop_control.open_chrome()
        ai_reply = re.sub(r"\[ACTION:\s*OPEN_CHROME\]", "", ai_reply, flags=re.IGNORECASE).strip()

    m_act_search = re.search(r"\[ACTION:\s*SEARCH_GOOGLE:\s*(.+?)\]", ai_reply, re.IGNORECASE)
    if m_act_search:
        q_search = m_act_search.group(1).strip()
        desktop_control.search_google(q_search)
        ai_reply = re.sub(r"\[ACTION:\s*SEARCH_GOOGLE:\s*.+?\]", "", ai_reply, flags=re.IGNORECASE).strip()

    m_act_music_play = re.search(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_PLAY:\s*(.+?)\]", ai_reply, re.IGNORECASE)
    if m_act_music_play:
        m_query = m_act_music_play.group(1).strip()
        music_player.play(query=m_query)
        ai_reply = re.sub(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_PLAY:\s*.+?\]", "", ai_reply, flags=re.IGNORECASE).strip()

    if re.search(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_PAUSE\]", ai_reply, re.IGNORECASE):
        music_player.pause()
        ai_reply = re.sub(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_PAUSE\]", "", ai_reply, flags=re.IGNORECASE).strip()

    if re.search(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_RESUME\]", ai_reply, re.IGNORECASE):
        music_player.resume()
        ai_reply = re.sub(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_RESUME\]", "", ai_reply, flags=re.IGNORECASE).strip()

    if re.search(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_NEXT\]", ai_reply, re.IGNORECASE):
        music_player.next_track()
        ai_reply = re.sub(r"\[ACTION:\s*(?:MUSIC|SPOTIFY)_NEXT\]", "", ai_reply, flags=re.IGNORECASE).strip()

    if re.search(r"\[ACTION:\s*MUSIC_STOP\]", ai_reply, re.IGNORECASE):
        music_player.stop()
        ai_reply = re.sub(r"\[ACTION:\s*MUSIC_STOP\]", "", ai_reply, flags=re.IGNORECASE).strip()

    m_act_vol = re.search(r"\[ACTION:\s*MUSIC_VOLUME:\s*(\d+)\]", ai_reply, re.IGNORECASE)
    if m_act_vol:
        vol = int(m_act_vol.group(1))
        music_player.set_volume(vol)
        ai_reply = re.sub(r"\[ACTION:\s*MUSIC_VOLUME:\s*\d+\]", "", ai_reply, flags=re.IGNORECASE).strip()

    m_act_img = re.search(r"\[ACTION:\s*(?:GENERATE_IMAGE|IMAGE_GENERATE|DRAW_IMAGE):\s*(.+?)\]", ai_reply, re.IGNORECASE)
    if m_act_img:
        img_prompt = m_act_img.group(1).strip()
        from backend.services.image_service import image_service
        img_res = image_service.generate_image(img_prompt)
        img_url = img_res.get("image_url", "")
        ai_reply = re.sub(r"\[ACTION:\s*(?:GENERATE_IMAGE|IMAGE_GENERATE|DRAW_IMAGE):\s*.+?\]", "", ai_reply, flags=re.IGNORECASE).strip()
        ai_reply += f"\n\n![{img_prompt}]({img_url})\n\n[Download Full-Res Picture]({img_url})"

    # Safety net: If LLM generated a local access refusal while user asked for a browser/system action, override it
    if any(phrase in ai_reply.lower() for phrase in ["don't have direct access to your local system", "cannot open applications or websites", "limited to data processing"]):
        retry_intent = intent_service.detect_and_execute(user_prompt)
        if retry_intent.is_handled:
            ai_reply = retry_intent.response_message

    msg_id = str(uuid.uuid4())
    serialized_citations = [c.model_dump() for c in citations] if citations else []

    # Step 5: Save to Database or fallback
    if db and _db_connected:
        try:
            # User message
            user_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conv_id,
                role="user",
                content=user_prompt,
                modality=request.modality
            )
            # Assistant message
            asst_msg = Message(
                id=msg_id,
                conversation_id=conv_id,
                role="assistant",
                content=ai_reply,
                modality="text",
                citations=json.dumps(serialized_citations) if serialized_citations else None,
                metadata_json=json.dumps({"viewer_actions": viewer_actions}) if viewer_actions else None
            )
            db.add(user_msg)
            db.add(asst_msg)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to persist chat messages to MySQL: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        # Fallback memory store
        conv_record = _fallback_conversations.get(conv_id)
        if conv_record:
            conv_record["updated_at"] = datetime.now(timezone.utc).isoformat()
            conv_record["messages"].append({
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": user_prompt,
                "modality": request.modality,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            conv_record["messages"].append({
                "id": msg_id,
                "role": "assistant",
                "content": ai_reply,
                "modality": "text",
                "citations": serialized_citations,
                "metadata_json": json.dumps({"viewer_actions": viewer_actions}) if viewer_actions else None,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

    return ChatResponse(
        conversation_id=conv_id,
        message_id=msg_id,
        response=ai_reply,
        reply=ai_reply,
        citations=citations,
        modality="text",
        status="success",
        viewer_actions=viewer_actions
    )

@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations():
    """Lists saved conversations from MySQL or in-memory fallback."""
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    convs = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
                    return [
                        ConversationSummary(
                            id=c.id,
                            title=c.title,
                            created_at=c.created_at.isoformat() if c.created_at else "",
                            updated_at=c.updated_at.isoformat() if c.updated_at else "",
                            message_count=len(c.messages)
                        )
                        for c in convs
                    ]
        except Exception as e:
            logger.warning(f"Error querying conversations from MySQL: {e}")

    # Fallback
    results = []
    for cid, data in sorted(_fallback_conversations.items(), key=lambda x: x[1]["updated_at"], reverse=True):
        results.append(ConversationSummary(
            id=cid,
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            message_count=len(data["messages"])
        ))
    return results

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str):
    """Retrieves full conversation details and chronological messages."""
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                    if conv:
                        messages = []
                        for m in conv.messages:
                            cits = None
                            if m.citations:
                                try:
                                    raw = json.loads(m.citations)
                                    cits = [Citation(**item) for item in raw]
                                except Exception:
                                    pass
                            messages.append(MessageDetail(
                                id=m.id,
                                role=m.role,
                                content=m.content,
                                modality=m.modality or "text",
                                citations=cits,
                                metadata_json=m.metadata_json,
                                created_at=m.created_at.isoformat() if m.created_at else ""
                            ))
                        return ConversationDetail(
                            id=conv.id,
                            title=conv.title,
                            created_at=conv.created_at.isoformat() if conv.created_at else "",
                            updated_at=conv.updated_at.isoformat() if conv.updated_at else "",
                            messages=messages
                        )
        except Exception as e:
            logger.warning(f"Error reading conversation {conversation_id}: {e}")

    # Fallback
    if conversation_id in _fallback_conversations:
        data = _fallback_conversations[conversation_id]
        messages = [
            MessageDetail(
                id=m["id"],
                role=m["role"],
                content=m["content"],
                modality=m.get("modality", "text"),
                citations=[Citation(**c) for c in m.get("citations", [])] if m.get("citations") else None,
                metadata_json=m.get("metadata_json"),
                created_at=m.get("created_at", "")
            )
            for m in data["messages"]
        ]
        return ConversationDetail(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages
        )

    raise HTTPException(status_code=404, detail="Conversation not found")

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str):
    """Deletes a conversation and its messages."""
    deleted = False
    if _db_connected:
        try:
            from backend.core.database import _SessionLocal
            if _SessionLocal:
                with _SessionLocal() as db:
                    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                    if conv:
                        db.delete(conv)
                        db.commit()
                        deleted = True
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id} from MySQL: {e}")

    if conversation_id in _fallback_conversations:
        del _fallback_conversations[conversation_id]
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"status": "success", "message": f"Conversation {conversation_id} deleted."}
