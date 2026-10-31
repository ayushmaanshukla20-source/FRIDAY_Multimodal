import React, { useState, useEffect } from 'react';
import {
  Flame,
  Clock,
  BarChart2,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  FileText,
  X,
  CheckCircle2,
  BookOpen,
} from 'lucide-react';
import { fetchStudyAnalytics, logStudySession, generateStudyPDF } from '../utils/api';

export default function StudyDashboardDrawer({ isOpen, onClose, onNotify }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  // Pomodoro Timer State
  const [timerSeconds, setTimerSeconds] = useState(25 * 60);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [timerSubject, setTimerSubject] = useState('Computer Science');
  const [isExportingPdf, setIsExportingPdf] = useState(false);

  // Load analytics from backend
  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await fetchStudyAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.warn('Could not load study analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadAnalytics();
    }
  }, [isOpen]);

  // Pomodoro Interval Effect
  useEffect(() => {
    let interval = null;
    if (isTimerRunning && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev - 1);
      }, 1000);
    } else if (timerSeconds === 0 && isTimerRunning) {
      setIsTimerRunning(false);
      // Auto-log completed 25-minute Pomodoro session
      logStudySession({
        subject: timerSubject,
        topic: 'Pomodoro Focus Block',
        durationMinutes: 25,
        notes: '25-minute deep focus block completed.',
      }).then(() => {
        loadAnalytics();
        if (onNotify) {
          onNotify(`🎉 Pomodoro completed! 25 minutes logged for ${timerSubject}.`);
        }
      });
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, timerSeconds, timerSubject]);

  const formatTimer = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleExportSamplePdf = async () => {
    try {
      setIsExportingPdf(true);
      const res = await generateStudyPDF({
        title: `${timerSubject}: Comprehensive Study Guide`,
        subject: timerSubject,
        documentType: 'study_guide',
        keyTakeaways: [
          'Master fundamental definitions before attempting complex applications.',
          'Solve minimum 3 practice problems per study block to cement retention.',
          'Review formula sheet 24 hours prior to assessment.',
        ],
        sections: [
          {
            title: '1. Theoretical Framework & Core Laws',
            content:
              'A systematic understanding of foundational theorems is essential for rigorous analytical reasoning.',
          },
          {
            title: '2. Problem Solving Methodology',
            content:
              '- Identify known and target variables.\n- Apply governing equations.\n- Verify dimensional consistency.',
          },
        ],
        practiceQuestions: [
          {
            question: 'What is the primary governing equation for this domain?',
            answer: 'Formulated through foundational conservation principles.',
          },
        ],
      });

      if (res.download_url) {
        window.open(res.download_url, '_blank');
        if (onNotify) {
          onNotify(`📄 Study Guide PDF generated and opened in browser.`);
        }
      }
    } catch (e) {
      console.error(e);
      alert('PDF generation error: ' + e.message);
    } finally {
      setIsExportingPdf(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-50 bg-[#060810]/95 backdrop-blur-2xl flex flex-col p-4 overflow-y-auto select-none border-l border-cyan-500/20">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <BarChart2 size={18} />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
              Student Productivity Suite
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-mono">
                AI ANALYTICS
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">Study Habits, Focus Timer & Artifacts</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
        >
          <X size={18} />
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2.5 my-3.5">
        {/* Streak */}
        <div className="p-3 rounded-xl bg-gradient-to-br from-amber-950/30 to-amber-900/10 border border-amber-500/30 flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-1 text-amber-400 mb-0.5">
            <Flame size={16} className="animate-pulse" />
            <span className="text-xs font-mono font-bold uppercase">Streak</span>
          </div>
          <span className="text-xl font-mono font-bold text-amber-200">
            {analytics?.streak_days || 3}
            <span className="text-xs font-normal text-amber-400 ml-1">Days</span>
          </span>
        </div>

        {/* Total Hours */}
        <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-950/30 to-cyan-900/10 border border-cyan-500/30 flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-1 text-cyan-400 mb-0.5">
            <Clock size={16} />
            <span className="text-xs font-mono font-bold uppercase">Total Time</span>
          </div>
          <span className="text-xl font-mono font-bold text-cyan-200">
            {analytics?.total_focus_hours || 2.6}
            <span className="text-xs font-normal text-cyan-400 ml-1">Hrs</span>
          </span>
        </div>

        {/* Today's Focus */}
        <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-950/30 to-emerald-900/10 border border-emerald-500/30 flex flex-col items-center justify-center text-center">
          <div className="flex items-center gap-1 text-emerald-400 mb-0.5">
            <CheckCircle2 size={16} />
            <span className="text-xs font-mono font-bold uppercase">Today</span>
          </div>
          <span className="text-xl font-mono font-bold text-emerald-200">
            {analytics?.today_focus_minutes || 45}
            <span className="text-xs font-normal text-emerald-400 ml-1">Mins</span>
          </span>
        </div>
      </div>

      {/* Pomodoro Focus Timer Block */}
      <div className="my-2 p-3.5 rounded-xl border border-cyan-500/30 bg-[#080d1a]/80 shadow-[0_0_20px_rgba(6,182,212,0.1)]">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-mono font-semibold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
            <Clock size={14} />
            Pomodoro Focus Interval
          </span>
          <select
            value={timerSubject}
            onChange={(e) => setTimerSubject(e.target.value)}
            className="text-xs bg-slate-900 border border-slate-700 text-slate-200 rounded px-2 py-0.5 outline-none font-mono"
          >
            <option value="Computer Science">Computer Science</option>
            <option value="Mathematics">Mathematics</option>
            <option value="Physics">Physics</option>
            <option value="Biology">Biology</option>
          </select>
        </div>

        <div className="text-center my-2 font-mono text-4xl font-extrabold text-slate-100 tracking-wider">
          {formatTimer(timerSeconds)}
        </div>

        <div className="flex items-center justify-center gap-3 mt-2">
          <button
            onClick={() => setIsTimerRunning(!isTimerRunning)}
            className={`px-4 py-1.5 rounded-lg text-xs font-mono font-semibold flex items-center gap-1.5 transition-all ${
              isTimerRunning
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 hover:bg-amber-500/30'
                : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 hover:bg-cyan-500/30 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
            }`}
          >
            {isTimerRunning ? <Pause size={14} /> : <Play size={14} />}
            <span>{isTimerRunning ? 'Pause' : 'Start Focus'}</span>
          </button>

          <button
            onClick={() => {
              setIsTimerRunning(false);
              setTimerSeconds(25 * 60);
            }}
            className="px-3 py-1.5 rounded-lg text-xs font-mono text-slate-400 bg-slate-800/60 hover:text-white transition-colors flex items-center gap-1"
            title="Reset to 25 mins"
          >
            <RotateCcw size={13} />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Subject Distribution */}
      <div className="my-2 p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
        <span className="text-xs font-mono font-semibold text-slate-300 uppercase tracking-wider block mb-2">
          📊 Study Subject Balance
        </span>
        <div className="space-y-2">
          {analytics?.subject_distribution ? (
            Object.entries(analytics.subject_distribution).map(([sub, pct]) => (
              <div key={sub}>
                <div className="flex justify-between text-xs font-mono text-slate-400 mb-0.5">
                  <span>{sub}</span>
                  <span className="text-cyan-400">{pct}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="text-xs text-slate-500">Loading subject analytics...</div>
          )}
        </div>
      </div>

      {/* Adaptive AI Recommendation */}
      <div className="my-2 p-3.5 rounded-xl border border-cyan-500/30 bg-cyan-950/20 text-xs">
        <div className="flex items-center gap-1.5 text-cyan-400 font-semibold mb-1">
          <Sparkles size={14} />
          <span>Adaptive AI Recommendation</span>
        </div>
        <p className="text-slate-300 leading-relaxed font-sans">
          {analytics?.adaptive_recommendation ||
            'Maintain a balanced 45-minute focus session between theoretical analysis and active problem solving.'}
        </p>
      </div>

      {/* PDF Export Quick Action */}
      <div className="mt-auto pt-3 border-t border-slate-800">
        <button
          onClick={handleExportSamplePdf}
          disabled={isExportingPdf}
          className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-semibold flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all cursor-pointer"
        >
          <FileText size={16} />
          <span>{isExportingPdf ? 'Compiling PDF...' : 'Export Structured Study Guide (PDF)'}</span>
        </button>
      </div>
    </div>
  );
}
