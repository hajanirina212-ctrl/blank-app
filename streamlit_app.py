import React, { useState, useEffect } from "react";
import { LayoutDashboard, Target, Flame, Calendar, Activity, BookOpen, BrainCircuit, Layers, ShieldCheck, Award, HelpCircle } from "lucide-react";

// Importer nos types
import { Goal, Habit, TimeBlock, Review, ProcrastinationLog, VisionBoard, UserStats, LifeDomain, Priority, Difficulty, TaskStatus, TimeBlockType, Project } from "./types";

// Importer nos sous-composants modulaires
import Dashboard from "./components/Dashboard";
import GoalsManager from "./components/GoalsManager";
import HabitsTracker from "./components/HabitsTracker";
import Planner from "./components/Planner";
import DisciplineCenter from "./components/DisciplineCenter";
import ReviewsManager from "./components/ReviewsManager";
import AIAdvisor from "./components/AIAdvisor";
import ArchitectureView from "./components/ArchitectureView";

export default function App() {
  const [activeTab, setActiveTab] = useState<"plan" | "goals" | "coach" | "settings">("plan");
  
  // États de sous-navigation pour garder l'application super simple d'accès
  const [goalsSubTab, setGoalsSubTab] = useState<"goals" | "habits">("goals");
  const [coachSubTab, setCoachSubTab] = useState<"advisor" | "discipline">("advisor");
  const [settingsSubTab, setSettingsSubTab] = useState<"planner" | "reviews" | "config">("planner");

  // State global
  const [stats, setStats] = useState<UserStats>({
    xp: 0,
    level: 1,
    unlockedBadges: [],
    disciplineScore: 0,
    deepWorkHoursTotal: 0,
    tasksCompletedTotal: 0,
    habitsCompletedTotal: 0,
    streakDays: 0
  });

  const [habits, setHabits] = useState<Habit[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [timeBlocks, setTimeBlocks] = useState<TimeBlock[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [procrastinationLogs, setProcrastinationLogs] = useState<ProcrastinationLog[]>([]);
  const [visionBoard, setVisionBoard] = useState<VisionBoard>({
    identity: "Devenir un créateur autonome et discipliné qui s'améliore de 1% par jour",
    longTermVision: "Publier mon chef-d'œuvre et vivre de ma liberté créative",
    oneYearVision: "Établir des rituels immuables de Deep Work et automatiser mes sources de revenus"
  });

  // Charger les données depuis localStorage au montage
  useEffect(() => {
    // 1. Charger la vision
    const savedVision = localStorage.getItem("kaizen_vision");
    if (savedVision) setVisionBoard(JSON.parse(savedVision));

    // 2. Charger les habitudes
    const savedHabits = localStorage.getItem("kaizen_habits");
    if (savedHabits) {
      setHabits(JSON.parse(savedHabits));
    } else {
      // Seeder des rituels par défaut (Atomic Habits) pour l'expérience initiale
      const defaultHabits: Habit[] = [
        {
          id: "h1",
          name: "Lecture réflexive",
          frequency: "daily",
          cue: "Dès que je ferme mon ordinateur à 18h",
          routine: "J'ouvre mon livre et lis 2 pages de philosophie",
          reward: "Je savoure une tasse d'infusion chaude",
          domain: LifeDomain.PERSONAL_GROWTH,
          history: [],
          streak: 0,
          bestStreak: 0,
          createdAt: new Date().toISOString()
        },
        {
          id: "h2",
          name: "Micro-méditation",
          frequency: "daily",
          cue: "Dès que mon premier café coule à 8h",
          routine: "Je fais 2 minutes de respiration diaphragmatique consciente",
          reward: "Je savoure la première gorgée de mon café",
          domain: LifeDomain.HEALTH,
          history: [],
          streak: 0,
          bestStreak: 0,
          createdAt: new Date().toISOString()
        }
      ];
      setHabits(defaultHabits);
      localStorage.setItem("kaizen_habits", JSON.stringify(defaultHabits));
    }

    // 3. Charger les objectifs
    const savedGoals = localStorage.getItem("kaizen_goals");
    if (savedGoals) {
      setGoals(JSON.parse(savedGoals));
    } else {
      // Seeder un objectif par défaut décomposé pour l'expérience initiale
      const defaultGoals: Goal[] = [
        {
          id: "g1",
          name: "Bâtir un système d'apprentissage autonome",
          description: "Mettre en place des outils d'études quotidiens sans surcharge cognitive",
          why: "Atteindre la liberté intellectuelle et professionnelle",
          startDate: new Date().toISOString().split("T")[0],
          targetDate: new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0], // +30 jours
          priority: Priority.HIGH,
          difficulty: Difficulty.MEDIUM,
          domain: LifeDomain.PERSONAL_GROWTH,
          progress: 0,
          projects: []
        }
      ];
      setGoals(defaultGoals);
      localStorage.setItem("kaizen_goals", JSON.stringify(defaultGoals));
    }

    // 4. Charger les blocs de temps
    const savedBlocks = localStorage.getItem("kaizen_blocks");
    if (savedBlocks) {
      setTimeBlocks(JSON.parse(savedBlocks));
    } else {
      const defaultBlocks: TimeBlock[] = [
        { id: "b1", title: "Planification Kaizen", startTime: "08:00", endTime: "08:15", dayOfWeek: new Date().getDay(), type: TimeBlockType.PLANNING },
        { id: "b2", title: "Travail Profond (Deep Work)", startTime: "09:00", endTime: "11:00", dayOfWeek: new Date().getDay(), type: TimeBlockType.DEEP_WORK, relatedGoalId: "g1" }
      ];
      setTimeBlocks(defaultBlocks);
      localStorage.setItem("kaizen_blocks", JSON.stringify(defaultBlocks));
    }

    // 5. Charger les revues
    const savedReviews = localStorage.getItem("kaizen_reviews");
    if (savedReviews) setReviews(JSON.parse(savedReviews));

    // 6. Charger les logs de procrastination
    const savedLogs = localStorage.getItem("kaizen_procrastination_logs");
    if (savedLogs) setProcrastinationLogs(JSON.parse(savedLogs));

    // 7. Charger les stats globales
    const savedStats = localStorage.getItem("kaizen_stats");
    if (savedStats) {
      setStats(JSON.parse(savedStats));
    } else {
      const initialStats = {
        xp: 0,
        level: 1,
        unlockedBadges: [],
        disciplineScore: 0,
        deepWorkHoursTotal: 0,
        tasksCompletedTotal: 0,
        habitsCompletedTotal: 0,
        streakDays: 0
      };
      setStats(initialStats);
      localStorage.setItem("kaizen_stats", JSON.stringify(initialStats));
    }
  }, []);

  // Recalculer l'indice de discipline en temps réel lorsque l'état change
  useEffect(() => {
    const todayStr = new Date().toISOString().split("T")[0];

    // C_habits component (35%)
    const dailyHabits = habits.filter(h => h.frequency === "daily");
    let c_habits = 0;
    if (dailyHabits.length > 0) {
      const doneCount = dailyHabits.filter(h => h.history.includes(todayStr)).length;
      c_habits = Math.round((doneCount / dailyHabits.length) * 100);
    }

    // C_tasks component (25%)
    let totalTasks = 0;
    let completedTasks = 0;
    goals.forEach(g => {
      g.projects.forEach(p => {
        p.stages.forEach(s => {
          s.tasks.forEach(t => {
            totalTasks++;
            if (t.status === TaskStatus.DONE) completedTasks++;
          });
        });
      });
    });
    const c_tasks = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    // C_deep_work component (25%)
    // Simple mock ratio pour les heures réelles vs prévues
    const c_deep_work = stats.deepWorkHoursTotal > 0 ? Math.min(100, Math.round((stats.deepWorkHoursTotal / 5) * 100)) : 0;

    // C_planning component (15%)
    const hasAnyRealProgress = stats.tasksCompletedTotal > 0 || stats.habitsCompletedTotal > 0 || stats.deepWorkHoursTotal > 0;
    const c_planning = (hasAnyRealProgress && timeBlocks.length > 0) ? Math.min(100, timeBlocks.length * 20) : 0;

    // Calcul pondéré
    const calculatedDiscipline = Math.round(
      (c_tasks * 0.25) + (c_habits * 0.35) + (c_deep_work * 0.25) + (c_planning * 0.15)
    );

    // Ajuster le score de discipline
    if (calculatedDiscipline !== stats.disciplineScore) {
      const updatedStats = { ...stats, disciplineScore: Math.max(0, Math.min(100, calculatedDiscipline)) };
      setStats(updatedStats);
      localStorage.setItem("kaizen_stats", JSON.stringify(updatedStats));
    }
  }, [habits, goals, timeBlocks, stats.deepWorkHoursTotal, stats.tasksCompletedTotal, stats.habitsCompletedTotal, stats.disciplineScore]);

  // Ajouter XP et gérer les montées de niveau
  const handleAddXP = (amount: number) => {
    let newXp = stats.xp + amount;
    let currentLevel = stats.level;
    let xpNeeded = Math.round(100 * Math.pow(currentLevel, 1.5));

    while (newXp >= xpNeeded) {
      newXp -= xpNeeded;
      currentLevel += 1;
      xpNeeded = Math.round(100 * Math.pow(currentLevel, 1.5));
      alert(`🎉 SENSEI : Félicitations ! Tu passes au Niveau ${currentLevel}. Ta discipline de 1% porte ses fruits.`);
    }

    const updated = {
      ...stats,
      xp: newXp,
      level: currentLevel,
      streakDays: amount === 15 ? stats.streakDays + 1 : stats.streakDays // simple incrémentation du streak sur habitude coche
    };
    setStats(updated);
    localStorage.setItem("kaizen_stats", JSON.stringify(updated));
  };

  // Callback Vision Board
  const handleUpdateVisionBoard = (vision: VisionBoard) => {
    setVisionBoard(vision);
    localStorage.setItem("kaizen_vision", JSON.stringify(vision));
  };

  // Callback Habitude toggling date
  const handleToggleHabitDate = (habitId: string, date: string) => {
    const updated = habits.map(h => {
      if (h.id !== habitId) return h;
      
      const exists = h.history.includes(date);
      let nextHistory = [];
      if (exists) {
        nextHistory = h.history.filter(d => d !== date);
      } else {
        nextHistory = [...h.history, date];
      }

      // Calcul simple du streak
      const currentStreak = !exists ? h.streak + 1 : Math.max(0, h.streak - 1);
      const bestStreak = Math.max(h.bestStreak, currentStreak);

      return {
        ...h,
        history: nextHistory,
        streak: currentStreak,
        bestStreak
      };
    });

    setHabits(updated);
    localStorage.setItem("kaizen_habits", JSON.stringify(updated));

    if (!habits.find(h => h.id === habitId)?.history.includes(date)) {
      // Si on vient de valider l'habitude, donner de l'XP
      handleAddXP(15);
      // Incrémenter l'historique global
      const updatedStats = { ...stats, habitsCompletedTotal: stats.habitsCompletedTotal + 1 };
      setStats(updatedStats);
      localStorage.setItem("kaizen_stats", JSON.stringify(updatedStats));
    }
  };

  // Callback Ajouter habitude
  const handleAddHabit = (newHabitData: Omit<Habit, "id" | "streak" | "bestStreak" | "history" | "createdAt">) => {
    const newHabit: Habit = {
      ...newHabitData,
      id: Math.random().toString(),
      streak: 0,
      bestStreak: 0,
      history: [],
      createdAt: new Date().toISOString()
    };

    const updated = [...habits, newHabit];
    setHabits(updated);
    localStorage.setItem("kaizen_habits", JSON.stringify(updated));
    handleAddXP(20); // +20 XP pour s'engager sur une habitude !
  };

  // Callback Ajouter objectif
  const handleAddGoal = (newGoal: Goal) => {
    const updated = [...goals, newGoal];
    setGoals(updated);
    localStorage.setItem("kaizen_goals", JSON.stringify(updated));
    handleAddXP(30); // +30 XP pour aligner un nouvel objectif !
  };

  // Callback Mettre à jour la progression de l'objectif
  const handleUpdateGoalProgress = (goalId: string, progress: number) => {
    const updated = goals.map(g => {
      if (g.id !== goalId) return g;
      return { ...g, progress };
    });
    setGoals(updated);
    localStorage.setItem("kaizen_goals", JSON.stringify(updated));
  };

  // Callback Mettre à jour les projets d'un objectif
  const handleUpdateGoalProjects = (goalId: string, projects: Project[]) => {
    const updated = goals.map(g => {
      if (g.id !== goalId) return g;
      return { ...g, projects };
    });
    setGoals(updated);
    localStorage.setItem("kaizen_goals", JSON.stringify(updated));
  };

  // Callback Time Blocking
  const handleAddTimeBlock = (block: TimeBlock) => {
    const updated = [...timeBlocks, block];
    setTimeBlocks(updated);
    localStorage.setItem("kaizen_blocks", JSON.stringify(updated));
    handleAddXP(10);
  };

  const handleDeleteTimeBlock = (blockId: string) => {
    const updated = timeBlocks.filter(b => b.id !== blockId);
    setTimeBlocks(updated);
    localStorage.setItem("kaizen_blocks", JSON.stringify(updated));
  };

  // Incrémenter les heures de Deep work réalisées
  const handleIncrementDeepWorkHours = (taskId: string, hours: number) => {
    // Parcourir et trouver la tâche dans l'arbre d'objectifs
    const updatedGoals = goals.map(g => {
      const updatedProjects = g.projects.map(p => {
        const updatedStages = p.stages.map(s => {
          const updatedTasks = s.tasks.map(t => {
            if (t.id !== taskId) return t;
            return {
              ...t,
              deepWorkHoursActual: t.deepWorkHoursActual + hours
            };
          });
          return { ...s, tasks: updatedTasks };
        });
        return { ...p, stages: updatedStages };
      });
      return { ...g, projects: updatedProjects };
    });

    setGoals(updatedGoals);
    localStorage.setItem("kaizen_goals", JSON.stringify(updatedGoals));

    // Incrémenter le total des heures de Deep Work
    const updatedStats = { ...stats, deepWorkHoursTotal: stats.deepWorkHoursTotal + hours };
    setStats(updatedStats);
    localStorage.setItem("kaizen_stats", JSON.stringify(updatedStats));
  };

  // Callback Bilan Rétrospectif
  const handleAddReview = (newReviewData: Omit<Review, "id" | "date" | "disciplineScore">) => {
    const newReview: Review = {
      ...newReviewData,
      id: Math.random().toString(),
      date: new Date().toISOString().split("T")[0],
      disciplineScore: stats.disciplineScore
    };

    const updated = [newReview, ...reviews];
    setReviews(updated);
    localStorage.setItem("kaizen_reviews", JSON.stringify(updated));
    handleAddXP(150); // Récompense de 150 XP pour la réflexion profonde !
  };

  // Callback Procrastination logs
  const handleAddProcrastinationLog = (log: ProcrastinationLog) => {
    const updated = [log, ...procrastinationLogs];
    setProcrastinationLogs(updated);
    localStorage.setItem("kaizen_procrastination_logs", JSON.stringify(updated));
    
    // Incrémenter le postponeCount de la tâche dans l'objectif
    const updatedGoals = goals.map(g => {
      const updatedProjects = g.projects.map(p => {
        const updatedStages = p.stages.map(s => {
          const updatedTasks = s.tasks.map(t => {
            if (t.id !== log.taskId) return t;
            return {
              ...t,
              postponeCount: t.postponeCount + 1
            };
          });
          return { ...s, tasks: updatedTasks };
        });
        return { ...p, stages: updatedStages };
      });
      return { ...g, projects: updatedProjects };
    });

    setGoals(updatedGoals);
    localStorage.setItem("kaizen_goals", JSON.stringify(updatedGoals));
  };

  const handleCompleteProcrastinationLog = (logId: string, taskId: string) => {
    const updatedLogs = procrastinationLogs.map(l => {
      if (l.id !== logId) return l;
      return { ...l, completed: true };
    });
    setProcrastinationLogs(updatedLogs);
    localStorage.setItem("kaizen_procrastination_logs", JSON.stringify(updatedLogs));

    // Marquer la tâche comme terminée (puisque le premier pas est fait et la résistance vaincue !)
    const updatedGoals = goals.map(g => {
      const updatedProjects = g.projects.map(p => {
        const updatedStages = p.stages.map(s => {
          const updatedTasks = s.tasks.map(t => {
            if (t.id !== taskId) return t;
            return {
              ...t,
              status: TaskStatus.DONE
            };
          });
          return { ...s, tasks: updatedTasks };
        });
        return { ...p, stages: updatedStages };
      });
      return { ...g, projects: updatedProjects };
    });

    setGoals(updatedGoals);
    localStorage.setItem("kaizen_goals", JSON.stringify(updatedGoals));
    
    // Increment total completed tasks
    setStats(prev => ({ ...prev, tasksCompletedTotal: prev.tasksCompletedTotal + 1 }));
  };

  // Basculer l'état d'une micro-tâche Kaizen au niveau global
  const handleToggleMicroTask = (goalId: string, projectId: string, stageId: string, taskId: string, microTaskId: string) => {
    const goal = goals.find(g => g.id === goalId);
    if (!goal) return;

    const updatedProjects = goal.projects.map(p => {
      if (p.id !== projectId) return p;

      const updatedStages = p.stages.map(s => {
        if (s.id !== stageId) return s;

        const updatedTasks = s.tasks.map(t => {
          if (t.id !== taskId) return t;

          const updatedMicroTasks = t.microTasks.map(mt => {
            if (mt.id !== microTaskId) return mt;
            const nextCompleted = !mt.completed;
            if (nextCompleted) handleAddXP(10); // +10 XP par micro-action Kaizen !
            return { ...mt, completed: nextCompleted };
          });

          // Si toutes les micro-tâches sont complétées, la tâche passe automatiquement à DONE
          const allDone = updatedMicroTasks.every(mt => mt.completed);
          const nextStatus = allDone ? TaskStatus.DONE : t.status === TaskStatus.DONE ? TaskStatus.IN_PROGRESS : t.status;

          return { ...t, microTasks: updatedMicroTasks, status: nextStatus };
        });

        const stageCompleted = updatedTasks.every(t => t.status === TaskStatus.DONE);
        return { ...s, tasks: updatedTasks, completed: stageCompleted };
      });

      const projectCompleted = updatedStages.every(s => s.completed);
      return { ...p, stages: updatedStages, completed: projectCompleted };
    });

    // Mettre à jour les projets de l'objectif
    const updatedGoals = goals.map(g => {
      if (g.id !== goalId) return g;
      
      // Calculer la progression
      let totalMT = 0;
      let completedMT = 0;
      updatedProjects.forEach(proj => {
        proj.stages.forEach(st => {
          st.tasks.forEach(tsk => {
            tsk.microTasks.forEach(mt => {
              totalMT++;
              if (mt.completed) completedMT++;
            });
          });
        });
      });
      const progress = totalMT > 0 ? Math.round((completedMT / totalMT) * 100) : 0;
      
      return { ...g, projects: updatedProjects, progress };
    });

    setGoals(updatedGoals);
    localStorage.setItem("kaizen_goals", JSON.stringify(updatedGoals));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col md:flex-row font-sans" id="app-container">
      {/* Sidebar gauche : Navigation unifiée */}
      <aside className="w-full md:w-64 bg-slate-900 border-b md:border-b-0 md:border-r border-slate-800 flex flex-col justify-between shrink-0" id="sidebar">
        <div>
          {/* Logo / Header */}
          <div className="p-6 border-b border-slate-800/80 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-600/15 border border-indigo-400/20 font-bold font-sans text-white text-base">
              K
            </div>
            <div>
              <h1 className="text-sm font-sans font-extrabold text-white tracking-tight uppercase">Kaizen Sensei</h1>
              <span className="text-[9px] font-mono text-indigo-400 tracking-wider">MÉTHODE 1% CONTINU</span>
            </div>
          </div>

          {/* Profil utilisateur rapide */}
          <div className="p-4 mx-4 my-4 bg-slate-950/80 rounded-xl border border-slate-800/50 flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center text-lg border border-slate-700/50">
              ⚔️
            </div>
            <div>
              <div className="text-xs font-bold text-white">Disciple Kaizen</div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="text-[10px] font-mono text-amber-400 font-bold">Niv. {stats.level}</span>
                <span className="text-slate-600 font-mono text-[9px]">•</span>
                <span className="text-[10px] text-slate-400 font-mono">{stats.xp} XP</span>
              </div>
            </div>
          </div>

          {/* Menus de navigation */}
          <nav className="px-3 space-y-1">
            <button
              onClick={() => setActiveTab("plan")}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${
                activeTab === "plan"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
              id="sidebar-btn-plan"
            >
              <LayoutDashboard className="w-4 h-4 shrink-0" />
              Mon Plan Quotidien
            </button>
            <button
              onClick={() => setActiveTab("goals")}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${
                activeTab === "goals"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
              id="sidebar-btn-goals"
            >
              <Target className="w-4 h-4 shrink-0" />
              Objectifs & Habitudes
            </button>
            <button
              onClick={() => setActiveTab("coach")}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-xs font-semibold transition-all text-left cursor-pointer ${
                activeTab === "coach"
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/15"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
              id="sidebar-btn-coach"
            >
              <BrainCircuit className="w-4 h-4 shrink-0 animate-pulse text-indigo-400" />
              Coach IA & Antidote
            </button>
          </nav>
        </div>

        {/* Pied de page de la barre latérale */}
        <div className="p-4 border-t border-slate-800/60 space-y-2">
          <button
            onClick={() => setActiveTab("settings")}
            className={`w-full flex items-center gap-2 px-4 py-2 rounded-lg text-[10px] font-mono tracking-wider uppercase transition-all text-left cursor-pointer ${
              activeTab === "settings"
                ? "bg-indigo-950/40 text-indigo-400 border border-indigo-800/40"
                : "text-slate-500 hover:text-slate-300"
            }`}
            id="sidebar-btn-settings"
          >
            <Layers className="w-3.5 h-3.5 shrink-0" />
            Réglages &amp; Specs
          </button>
          <div className="text-[9px] text-slate-600 font-mono text-center">
            SENSEI PROTOCOL v1.0 • © 2026
          </div>
        </div>
      </aside>

      {/* Contenu principal */}
      <main className="flex-1 p-6 md:p-8 overflow-y-auto max-h-screen space-y-6" id="main-content-area">
        {/* En-tête rapide d'information globale de l'utilisateur */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-4 border-b border-slate-900" id="global-header">
          <div>
            <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest font-bold">SYSTÈME COMPORTEMENTAL KAIZEN</span>
            <h2 className="text-xl font-sans font-bold text-white tracking-tight">Atteindre n'importe quel objectif de 1% en 1%</h2>
          </div>
          <div className="flex gap-4 items-center">
            <div className="text-right">
              <span className="text-[9px] text-slate-500 uppercase font-mono">Discipline globale :</span>
              <span className={`text-sm font-mono font-bold block ${stats.disciplineScore >= 75 ? "text-emerald-400" : stats.disciplineScore >= 50 ? "text-indigo-400" : "text-amber-500"}`}>
                {stats.disciplineScore} %
              </span>
            </div>
            <div className="w-px h-8 bg-slate-800"></div>
            <div className="text-right">
              <span className="text-[9px] text-slate-500 uppercase font-mono">Série en cours :</span>
              <span className="text-sm font-mono font-bold text-amber-500 block">
                🔥 {stats.streakDays} jours
              </span>
            </div>
          </div>
        </header>

        {/* Route views */}
        <div className="animate-fade-in" id="active-tab-content-container">
          {activeTab === "plan" && (
            <Dashboard
              stats={stats}
              habits={habits}
              goals={goals}
              visionBoard={visionBoard}
              onUpdateVisionBoard={handleUpdateVisionBoard}
              onToggleHabit={handleToggleHabitDate}
              onAddXP={handleAddXP}
              onToggleMicroTask={handleToggleMicroTask}
            />
          )}

          {activeTab === "goals" && (
            <div className="space-y-4">
              {/* Onglets de sous-navigation */}
              <div className="flex gap-2 border-b border-slate-800/80 pb-3 overflow-x-auto">
                <button
                  onClick={() => setGoalsSubTab("goals")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    goalsSubTab === "goals"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  🎯 Mes Objectifs &amp; Décompositions Kaizen
                </button>
                <button
                  onClick={() => setGoalsSubTab("habits")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    goalsSubTab === "habits"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  🔥 Rituels &amp; Habitudes Atomiques
                </button>
              </div>

              <div className="mt-2">
                {goalsSubTab === "goals" ? (
                  <GoalsManager
                    goals={goals}
                    onAddGoal={handleAddGoal}
                    onUpdateGoalProgress={handleUpdateGoalProgress}
                    onUpdateGoalProjects={handleUpdateGoalProjects}
                    onAddXP={handleAddXP}
                    onAddHabit={handleAddHabit}
                  />
                ) : (
                  <HabitsTracker
                    habits={habits}
                    onAddHabit={handleAddHabit}
                    onToggleHabitDate={handleToggleHabitDate}
                  />
                )}
              </div>
            </div>
          )}

          {activeTab === "coach" && (
            <div className="space-y-4">
              {/* Onglets de sous-navigation */}
              <div className="flex gap-2 border-b border-slate-800/80 pb-3 overflow-x-auto">
                <button
                  onClick={() => setCoachSubTab("advisor")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    coachSubTab === "advisor"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  💬 S'entretenir avec le Sensei IA
                </button>
                <button
                  onClick={() => setCoachSubTab("discipline")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    coachSubTab === "discipline"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  ⚡ Antidote Anti-Procrastination ("J'ai la flemme !")
                </button>
              </div>

              <div className="mt-2">
                {coachSubTab === "advisor" ? (
                  <AIAdvisor
                    stats={stats}
                    habits={habits}
                    goals={goals}
                    procrastinationLogs={procrastinationLogs}
                    identity={visionBoard.identity}
                    onAddXP={handleAddXP}
                  />
                ) : (
                  <DisciplineCenter
                    stats={stats}
                    goals={goals}
                    procrastinationLogs={procrastinationLogs}
                    onAddProcrastinationLog={handleAddProcrastinationLog}
                    onCompleteProcrastinationLog={handleCompleteProcrastinationLog}
                    onAddXP={handleAddXP}
                  />
                )}
              </div>
            </div>
          )}

          {activeTab === "settings" && (
            <div className="space-y-4">
              {/* Onglets de sous-navigation */}
              <div className="flex gap-2 border-b border-slate-800/80 pb-3 overflow-x-auto">
                <button
                  onClick={() => setSettingsSubTab("planner")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    settingsSubTab === "planner"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  📅 Agenda &amp; Time Blocking
                </button>
                <button
                  onClick={() => setSettingsSubTab("reviews")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    settingsSubTab === "reviews"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  📊 Bilans Rétrospectifs
                </button>
                <button
                  onClick={() => setSettingsSubTab("config")}
                  className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all shrink-0 cursor-pointer ${
                    settingsSubTab === "config"
                      ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/40"
                  }`}
                >
                  ⚙️ Spécifications &amp; Données
                </button>
              </div>

              <div className="mt-2">
                {settingsSubTab === "planner" && (
                  <Planner
                    timeBlocks={timeBlocks}
                    goals={goals}
                    onAddTimeBlock={handleAddTimeBlock}
                    onDeleteTimeBlock={handleDeleteTimeBlock}
                    onIncrementDeepWorkHours={handleIncrementDeepWorkHours}
                    onAddXP={handleAddXP}
                  />
                )}

                {settingsSubTab === "reviews" && (
                  <ReviewsManager
                    reviews={reviews}
                    stats={stats}
                    onAddReview={handleAddReview}
                  />
                )}

                {settingsSubTab === "config" && (
                  <ArchitectureView
                    stats={stats}
                    goals={goals}
                    habits={habits}
                    procrastinationLogs={procrastinationLogs}
                    timeBlocks={timeBlocks}
                    reviews={reviews}
                    onResetAllData={() => {
                      if (confirm("Êtes-vous sûr de vouloir supprimer toutes vos données ? Cette action est irréversible.")) {
                        localStorage.clear();
                        window.location.reload();
                      }
                    }}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
