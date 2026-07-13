import React, { useState } from "react";
import { Plus, Target, Calendar, Award, Sparkles, CheckCircle2, Circle, ChevronRight, ChevronDown, ListTodo, Loader2, ArrowRight, Database, HelpCircle, ShieldCheck, Trash2, Settings, Info } from "lucide-react";
import { Goal, LifeDomain, Priority, Difficulty, TaskStatus, KaizenMicroTask, Project, ProjectStage, Task } from "../types";

interface GoalsManagerProps {
  goals: Goal[];
  onAddGoal: (goal: Goal) => void;
  onUpdateGoalProgress: (goalId: string, progress: number) => void;
  onUpdateGoalProjects: (goalId: string, projects: Project[]) => void;
  onAddXP: (amount: number) => void;
}

export default function GoalsManager({
  goals,
  onAddGoal,
  onUpdateGoalProgress,
  onUpdateGoalProjects,
  onAddXP
}: GoalsManagerProps) {
  const [showAddForm, setShowAddForm] = useState<boolean>(false);
  const [selectedGoalId, setSelectedGoalId] = useState<string | null>(goals.length > 0 ? goals[0].id : null);
  const [decomposingGoalId, setDecomposingGoalId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"simple" | "advanced">("simple");
  const [newMicroTaskName, setNewMicroTaskName] = useState<string>("");

  // Form states
  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [why, setWhy] = useState<string>("");
  const [targetDate, setTargetDate] = useState<string>("");
  const [priority, setPriority] = useState<Priority>(Priority.MEDIUM);
  const [difficulty, setDifficulty] = useState<Difficulty>(Difficulty.MEDIUM);
  const [domain, setDomain] = useState<LifeDomain>(LifeDomain.CAREER);

  const handleCreateGoal = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !why || !targetDate) {
      alert("S'il te plaît, remplis toutes les informations de l'objectif.");
      return;
    }

    const newGoal: Goal = {
      id: Math.random().toString(),
      name,
      description,
      why,
      startDate: new Date().toISOString().split("T")[0],
      targetDate,
      priority,
      difficulty,
      domain,
      progress: 0,
      projects: []
    };

    onAddGoal(newGoal);
    setSelectedGoalId(newGoal.id); // Ouvrir immédiatement
    setName("");
    setDescription("");
    setWhy("");
    setTargetDate("");
    setShowAddForm(false);
  };

  // Lancer la décomposition automatique de l'objectif par l'IA
  const handleAIDecompose = async (goalId: string) => {
    const goal = goals.find(g => g.id === goalId);
    if (!goal) return;

    setDecomposingGoalId(goalId);

    try {
      const response = await fetch("/api/ai/decompose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goalName: goal.name,
          goalDescription: goal.description,
          domain: goal.domain,
          priority: goal.priority,
          difficulty: goal.difficulty,
          why: goal.why
        })
      });

      if (!response.ok) {
        throw new Error("Impossible de joindre le serveur d'IA.");
      }

      const data = await response.json();

      // Convertir la réponse IA au format de types attendu
      const newProject: Project = {
        id: Math.random().toString(),
        name: data.projectName || `Projet Kaizen - ${goal.name}`,
        description: data.projectDescription || "",
        completed: false,
        stages: (data.stages || []).map((stage: any, sIdx: number) => ({
          id: `stage-${sIdx}-${Math.random()}`,
          name: stage.name,
          description: stage.description,
          completed: false,
          tasks: (stage.tasks || []).map((task: any, tIdx: number) => ({
            id: `task-${sIdx}-${tIdx}-${Math.random()}`,
            name: task.name,
            description: task.description,
            status: TaskStatus.TODO,
            postponeCount: 0,
            deepWorkHoursPlanned: task.deepWorkHoursPlanned || 1,
            deepWorkHoursActual: 0,
            dueDate: goal.targetDate,
            microTasks: (task.microTasks || []).map((mt: any, mIdx: number) => ({
              id: `mt-${sIdx}-${tIdx}-${mIdx}-${Math.random()}`,
              name: mt.name,
              completed: false
            }))
          }))
        }))
      };

      onUpdateGoalProjects(goalId, [newProject]);
      onAddXP(100); // Gagne de l'XP pour avoir initialisé le plan d'action !
      
      // Recalculer le pourcentage
      recalculateProgressForGoal(goalId, [newProject]);
    } catch (error: any) {
      console.error(error);
      alert("Erreur de décomposition IA : " + error.message);
    } finally {
      setDecomposingGoalId(null);
    }
  };

  // Recalculer le pourcentage de progression global basé sur les micro-tâches complétées
  const recalculateProgressForGoal = (goalId: string, updatedProjects: Project[]) => {
    let totalMT = 0;
    let completedMT = 0;
    updatedProjects.forEach(p => {
      p.stages.forEach(s => {
        s.tasks.forEach(t => {
          t.microTasks.forEach(mt => {
            totalMT++;
            if (mt.completed) completedMT++;
          });
        });
      });
    });

    const newProgress = totalMT > 0 ? Math.round((completedMT / totalMT) * 100) : 0;
    onUpdateGoalProgress(goalId, newProgress);
  };

  // Basculer l'état d'une micro-tâche Kaizen
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
            if (nextCompleted) onAddXP(10); // +10 XP par micro-action Kaizen !
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

    onUpdateGoalProjects(goalId, updatedProjects);
    recalculateProgressForGoal(goalId, updatedProjects);
  };

  // Ajouter une micro-tâche personnalisée directement dans l'interface simple
  const handleAddCustomMicroTask = (goalId: string) => {
    if (!newMicroTaskName.trim()) return;
    const goal = goals.find(g => g.id === goalId);
    if (!goal) return;

    let updatedProjects = goal.projects ? [...goal.projects] : [];
    
    if (updatedProjects.length === 0) {
      updatedProjects = [{
        id: "proj-" + Math.random().toString(36).substr(2, 9),
        name: `Plan d'action - ${goal.name}`,
        description: "Généré automatiquement pour stocker vos micro-actions",
        completed: false,
        stages: [{
          id: "stage-" + Math.random().toString(36).substr(2, 9),
          name: "Vos Actions Prioritaires",
          description: "La philosophie Kaizen du pas à pas",
          completed: false,
          tasks: [{
            id: "task-" + Math.random().toString(36).substr(2, 9),
            name: "Micro-Tâches",
            description: "Actions rapides",
            status: TaskStatus.TODO,
            postponeCount: 0,
            deepWorkHoursPlanned: 1,
            deepWorkHoursActual: 0,
            dueDate: goal.targetDate,
            microTasks: []
          }]
        }]
      }];
    }

    const updated = updatedProjects.map((p, pIdx) => {
      if (pIdx !== 0) return p;
      return {
        ...p,
        stages: p.stages.map((s, sIdx) => {
          if (sIdx !== 0) return s;
          return {
            ...s,
            tasks: s.tasks.map((t, tIdx) => {
              if (tIdx !== 0) return t;
              return {
                ...t,
                microTasks: [
                  ...t.microTasks,
                  {
                    id: "mt-" + Math.random().toString(36).substr(2, 9),
                    name: newMicroTaskName.trim(),
                    completed: false
                  }
                ]
              };
            })
          };
        })
      };
    });

    onUpdateGoalProjects(goalId, updated);
    setNewMicroTaskName("");
    onAddXP(5); // +5 XP pour l'autodiscipline d'ajouter ses tâches
    recalculateProgressForGoal(goalId, updated);
  };

  // Basculer le statut d'une tâche principale
  const handleToggleTaskStatus = (goalId: string, projectId: string, stageId: string, taskId: string) => {
    const goal = goals.find(g => g.id === goalId);
    if (!goal) return;

    const updatedProjects = goal.projects.map(p => {
      if (p.id !== projectId) return p;

      const updatedStages = p.stages.map(s => {
        if (s.id !== stageId) return s;

        const updatedTasks = s.tasks.map(t => {
          if (t.id !== taskId) return t;
          const nextStatus = t.status === TaskStatus.DONE ? TaskStatus.TODO : TaskStatus.DONE;
          
          // Mettre également à jour toutes les micro-tâches
          const updatedMicroTasks = t.microTasks.map(mt => ({
            ...mt,
            completed: nextStatus === TaskStatus.DONE
          }));

          if (nextStatus === TaskStatus.DONE) onAddXP(30); // +30 XP pour une tâche principale !

          return { ...t, status: nextStatus, microTasks: updatedMicroTasks };
        });

        const stageCompleted = updatedTasks.every(t => t.status === TaskStatus.DONE);
        return { ...s, tasks: updatedTasks, completed: stageCompleted };
      });

      return { ...p, stages: updatedStages };
    });

    onUpdateGoalProjects(goalId, updatedProjects);
    recalculateProgressForGoal(goalId, updatedProjects);
  };

  // Extraire toutes les micro-tâches de l'objectif sous forme de liste plate
  const getFlatMicroTasks = (goal: Goal) => {
    const flatList: {
      id: string;
      name: string;
      completed: boolean;
      projectId: string;
      stageId: string;
      taskId: string;
    }[] = [];

    goal.projects?.forEach(p => {
      p.stages?.forEach(s => {
        s.tasks?.forEach(t => {
          t.microTasks?.forEach(mt => {
            flatList.push({
              id: mt.id,
              name: mt.name,
              completed: mt.completed,
              projectId: p.id,
              stageId: s.id,
              taskId: t.id
            });
          });
        });
      });
    });

    return flatList;
  };

  return (
    <div className="space-y-6" id="goals-manager-root">
      {/* En-tête de la page */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/50 rounded-2xl border border-slate-800 p-6 backdrop-blur-sm shadow-xl">
        <div>
          <h2 className="text-xl font-sans font-bold text-white tracking-tight flex items-center gap-2">
            <Target className="text-indigo-400 w-5 h-5 animate-pulse" />
            Gestion d'Objectifs Simplifiée par l'IA
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Déclarez vos objectifs. L'IA s'occupe de concevoir instantanément vos micro-tâches de moins de 15 minutes.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode(viewMode === "simple" ? "advanced" : "simple")}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-mono px-3.5 py-2 rounded-xl border border-slate-700 transition-all cursor-pointer"
            id="btn-toggle-view-mode"
            title="Basculer entre la vue simplifiée et la vue projets complexes"
          >
            <Settings className="w-3.5 h-3.5" />
            {viewMode === "simple" ? "Mode Avancé" : "Mode Simple (Conseillé)"}
          </button>
          {!showAddForm && (
            <button
              onClick={() => setShowAddForm(true)}
              className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md hover:shadow-indigo-600/10 transition-all cursor-pointer"
              id="btn-open-goal-form"
            >
              <Plus className="w-3.5 h-3.5" />
              Nouvel Objectif
            </button>
          )}
        </div>
      </div>

      {/* Formulaire d'ajout d'objectif */}
      {showAddForm && (
        <form onSubmit={handleCreateGoal} className="bg-slate-900/50 rounded-2xl border border-slate-800 p-6 backdrop-blur-sm shadow-xl space-y-4" id="form-add-goal">
          <h3 className="text-sm font-sans font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2.5">
            Ajouter un Objectif
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Nom de l'objectif</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ex: Lancer mon propre site internet, apprendre l'anglais, faire du sport..."
                  className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 outline-none transition-all placeholder:text-slate-600"
                  required
                  id="input-goal-name"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Description optionnelle</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Expliquez brièvement ce que vous souhaitez accomplir..."
                  className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 outline-none transition-all placeholder:text-slate-600 h-24"
                  id="input-goal-desc"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Pourquoi cet objectif est capital pour vous ? (Motivation profonde)</label>
                <input
                  type="text"
                  value={why}
                  onChange={(e) => setWhy(e.target.value)}
                  placeholder="Ex: Pour me sentir plus indépendant financièrement et libre de mon temps."
                  className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 outline-none transition-all placeholder:text-slate-600"
                  required
                  id="input-goal-why"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Date limite souhaitée</label>
                  <input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 outline-none transition-all"
                    required
                    id="input-goal-target-date"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1.5">Catégorie de vie</label>
                  <select
                    value={domain}
                    onChange={(e) => setDomain(e.target.value as LifeDomain)}
                    className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-2 py-2 outline-none transition-all"
                    id="select-goal-domain"
                  >
                    {Object.values(LifeDomain).map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-800/80 pt-4">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="text-xs font-semibold text-slate-400 bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl transition-all cursor-pointer"
              id="btn-cancel-goal"
            >
              Annuler
            </button>
            <button
              type="submit"
              className="text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
              id="btn-submit-goal"
            >
              Créer l'Objectif
            </button>
          </div>
        </form>
      )}

      {/* Colonne gauche (liste) et droite (détails) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Liste des objectifs */}
        <div className="lg:col-span-4 space-y-4">
          <h3 className="text-xs font-sans font-bold text-slate-300 uppercase tracking-wider">Vos Objectifs</h3>
          {goals.length === 0 ? (
            <div className="bg-slate-900/30 rounded-xl border border-slate-800/80 p-6 text-center">
              <Target className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-xs text-slate-400">Aucun objectif créé pour le moment.</p>
              <button
                onClick={() => setShowAddForm(true)}
                className="mt-3 text-[11px] font-bold text-indigo-400 hover:text-indigo-300 cursor-pointer"
              >
                + En créer un maintenant
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {goals.map((goal) => {
                const isSelected = selectedGoalId === goal.id;
                const flatMT = getFlatMicroTasks(goal);
                const doneMT = flatMT.filter(m => m.completed).length;

                return (
                  <div
                    key={goal.id}
                    onClick={() => setSelectedGoalId(goal.id)}
                    className={`bg-slate-900/50 rounded-xl border p-4 shadow-sm hover:border-indigo-500/30 cursor-pointer transition-all flex flex-col justify-between ${
                      isSelected ? "border-indigo-500 bg-indigo-950/10 shadow-indigo-950/20" : "border-slate-800"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-[9px] font-mono text-indigo-400 bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-900/30">{goal.domain}</span>
                        <span className="text-[9px] font-mono text-slate-500">Cible : {goal.targetDate}</span>
                      </div>
                      <h4 className="text-xs font-bold text-white line-clamp-1">{goal.name}</h4>
                      <p className="text-[10px] text-slate-400 mt-1 line-clamp-1 italic">« {goal.why} »</p>
                    </div>

                    <div className="space-y-1.5 pt-3 mt-3 border-t border-slate-800/60">
                      <div className="flex justify-between items-center text-[10px] font-mono">
                        <span className="text-slate-500">
                          {flatMT.length > 0 ? `${doneMT} / ${flatMT.length} micro-tâches` : "Aucune tâche"}
                        </span>
                        <span className="font-bold text-indigo-400">{goal.progress}%</span>
                      </div>
                      <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full transition-all duration-500" style={{ width: `${goal.progress}%` }}></div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Détails de l'objectif sélectionné */}
        <div className="lg:col-span-8 bg-slate-900/50 rounded-2xl border border-slate-800 p-6 backdrop-blur-sm shadow-xl min-h-[450px] flex flex-col justify-between">
          {selectedGoalId ? (
            (() => {
              const goal = goals.find(g => g.id === selectedGoalId);
              if (!goal) return <p className="text-xs text-slate-500 m-auto">Sélectionnez un objectif à gauche pour l'afficher.</p>;

              const flatMT = getFlatMicroTasks(goal);
              const hasProjects = goal.projects && goal.projects.length > 0;

              return (
                <div className="space-y-6 flex-1 flex flex-col justify-between">
                  <div className="space-y-5">
                    {/* Infos de base */}
                    <div className="border-b border-slate-800 pb-4">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-widest font-bold">Plan d'Action Kaizen</span>
                        <span className="text-[10px] font-mono text-slate-500">Date limite : {goal.targetDate}</span>
                      </div>
                      <h3 className="text-base font-bold text-white mt-1">{goal.name}</h3>
                      {goal.description && <p className="text-xs text-slate-400 mt-1.5">{goal.description}</p>}
                      <div className="bg-slate-950 p-3 rounded-xl border border-slate-850 text-xs text-slate-300 italic mt-3 flex items-start gap-2">
                        <span className="text-amber-500 font-bold shrink-0">Mon WHY profond :</span>
                        <span>« {goal.why} »</span>
                      </div>
                    </div>

                    {/* VUE SIMPLE (FLAT LIST OF TASKS) */}
                    {viewMode === "simple" && (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-mono text-slate-300 uppercase tracking-wider font-semibold flex items-center gap-1.5">
                            <ListTodo className="w-4 h-4 text-indigo-400" />
                            Mes micro-tâches de moins de 15 min
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {flatMT.length} actions programmées
                          </span>
                        </div>

                        {flatMT.length > 0 ? (
                          <div className="bg-slate-950/50 rounded-xl border border-slate-850 p-3.5 space-y-2 max-h-[300px] overflow-y-auto">
                            {flatMT.map((mt) => (
                              <div
                                key={mt.id}
                                className="flex items-center justify-between gap-3 p-2 bg-slate-900/40 rounded-lg border border-slate-800/40 hover:border-slate-800 transition-all"
                              >
                                <button
                                  onClick={() => handleToggleMicroTask(goal.id, mt.projectId, mt.stageId, mt.taskId, mt.id)}
                                  className="flex items-center gap-2.5 text-xs text-slate-300 hover:text-white cursor-pointer text-left w-full"
                                  id={`btn-flat-mt-${mt.id}`}
                                >
                                  {mt.completed ? (
                                    <CheckCircle2 className="w-4.5 h-4.5 text-indigo-500 shrink-0" />
                                  ) : (
                                    <Circle className="w-4.5 h-4.5 text-slate-700 hover:text-slate-500 shrink-0" />
                                  )}
                                  <span className={mt.completed ? "line-through text-slate-500" : "text-slate-200"}>
                                    {mt.name}
                                  </span>
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8 bg-slate-950/20 border border-dashed border-slate-800 rounded-xl">
                            <Sparkles className="w-8 h-8 text-indigo-500/40 mx-auto mb-2" />
                            <p className="text-xs text-slate-300">Aucune tâche active pour cet objectif.</p>
                            <p className="text-[10px] text-slate-500 mt-1 max-w-xs mx-auto">
                              Cliquez ci-dessous pour laisser l'IA Sensei concevoir instantanément un plan de micro-actions de moins de 15 minutes.
                            </p>
                          </div>
                        )}

                        {/* Formulaire pour ajouter une tâche personnalisée à la liste */}
                        <div className="flex gap-2 mt-4">
                          <input
                            type="text"
                            value={newMicroTaskName}
                            onChange={(e) => setNewMicroTaskName(e.target.value)}
                            placeholder="➕ Ajouter ma propre micro-action de 15 min..."
                            className="w-full bg-slate-950 text-xs text-white border border-slate-800 focus:border-indigo-500 rounded-xl px-4 py-2.5 outline-none transition-all placeholder:text-slate-600"
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                e.preventDefault();
                                handleAddCustomMicroTask(goal.id);
                              }
                            }}
                            id="input-simple-mt-name"
                          />
                          <button
                            onClick={() => handleAddCustomMicroTask(goal.id)}
                            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 rounded-xl border border-slate-700 cursor-pointer transition-all whitespace-nowrap"
                          >
                            Ajouter
                          </button>
                        </div>
                      </div>
                    )}

                    {/* VUE AVANCÉE (PROJETS -> STAGES -> TASKS) */}
                    {viewMode === "advanced" && (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider font-semibold">PLAN D'ACTION STRUCTURÉ DÉTAILLÉ</span>
                          <span className="text-[10px] text-slate-500">1 Projet • 3 Étapes • Tâches</span>
                        </div>

                        {hasProjects ? (
                          goal.projects.map((proj) => (
                            <div key={proj.id} className="space-y-4">
                              <div className="bg-slate-950/60 px-4 py-3 rounded-xl border border-indigo-950/40">
                                <h4 className="text-xs font-bold text-white">Projet : {proj.name}</h4>
                                <p className="text-[10px] text-slate-400 mt-1 italic">{proj.description}</p>
                              </div>

                              <div className="space-y-3">
                                {proj.stages.map((stage) => (
                                  <div key={stage.id} className="bg-slate-800/10 border border-slate-800/80 rounded-xl p-4 space-y-3">
                                    <div className="flex items-center justify-between border-b border-slate-800/60 pb-2">
                                      <div className="text-xs font-bold text-white flex items-center gap-1.5">
                                        <div className={`w-2 h-2 rounded-full ${stage.completed ? "bg-emerald-500" : "bg-indigo-400"}`}></div>
                                        {stage.name}
                                      </div>
                                      <span className="text-[9px] text-slate-500">{stage.description}</span>
                                    </div>

                                    <div className="space-y-2.5">
                                      {stage.tasks.map((task) => {
                                        const isDone = task.status === TaskStatus.DONE;
                                        return (
                                          <div key={task.id} className="bg-slate-900/60 rounded-xl border border-slate-800 p-3 space-y-2">
                                            <div className="flex items-center justify-between">
                                              <button
                                                onClick={() => handleToggleTaskStatus(goal.id, proj.id, stage.id, task.id)}
                                                className="flex items-center gap-2 text-xs font-semibold text-slate-200 hover:text-white cursor-pointer text-left"
                                                id={`btn-task-toggle-${task.id}`}
                                              >
                                                {isDone ? (
                                                  <CheckCircle2 className="w-4.5 h-4.5 text-emerald-500 shrink-0" />
                                                ) : (
                                                  <Circle className="w-4.5 h-4.5 text-slate-700 hover:text-slate-500 shrink-0" />
                                                )}
                                                <span className={isDone ? "line-through text-slate-500" : ""}>{task.name}</span>
                                              </button>
                                              <span className="text-[9px] font-mono text-slate-500 uppercase tracking-wider bg-slate-800 px-1.5 py-0.5 rounded">
                                                Deep Work : {task.deepWorkHoursPlanned}h
                                              </span>
                                            </div>

                                            <div className="pl-6.5 space-y-1.5 border-l border-slate-800/60 ml-2 pt-1">
                                              {task.microTasks.map((mt) => (
                                                <button
                                                  key={mt.id}
                                                  onClick={() => handleToggleMicroTask(goal.id, proj.id, stage.id, task.id, mt.id)}
                                                  className="flex items-center gap-2 text-[10px] text-slate-400 hover:text-slate-200 w-full text-left cursor-pointer"
                                                  id={`btn-micro-toggle-${mt.id}`}
                                                >
                                                  {mt.completed ? (
                                                    <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                                                  ) : (
                                                    <Circle className="w-3.5 h-3.5 text-slate-800 hover:text-slate-700 shrink-0" />
                                                  )}
                                                  <span className={mt.completed ? "line-through text-slate-600" : ""}>{mt.name}</span>
                                                </button>
                                              ))}
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-6">
                            <p className="text-xs text-slate-500 italic">Aucun projet structuré. Utilisez le bouton IA ci-dessous.</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Bouton IA de décomposition si pas encore de tâches */}
                    {flatMT.length === 0 && (
                      <div className="text-center py-4 flex flex-col items-center justify-center m-auto max-w-sm mt-4">
                        <button
                          onClick={() => handleAIDecompose(goal.id)}
                          disabled={decomposingGoalId === goal.id}
                          className="inline-flex items-center gap-2 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-850 disabled:text-slate-500 text-white px-6 py-3 rounded-xl shadow-lg hover:shadow-indigo-600/15 cursor-pointer transition-all"
                          id="btn-ai-decompose"
                        >
                          {decomposingGoalId === goal.id ? (
                            <>
                              <Loader2 className="w-4 h-4 animate-spin" />
                              L'IA conçoit vos micro-tâches (moins de 15 min)...
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-4 h-4 animate-pulse" />
                              🤖 Décomposer par l'IA (+100 XP)
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>

                  {/* INFO ENCADRÉ BASE DE DONNÉES (RÉPONSE CLAIRE À LA QUESTION DE L'UTILISATEUR) */}
                  <div className="mt-8 bg-slate-950/60 rounded-xl border border-slate-800/80 p-4 space-y-2">
                    <h4 className="text-xs font-bold text-indigo-400 flex items-center gap-2">
                      <Database className="w-4 h-4 text-indigo-400" />
                      🗄️ Où se trouve notre base de données ?
                    </h4>
                    <div className="text-[11px] text-slate-400 space-y-1.5 leading-relaxed">
                      <p>
                        Vos données sont sauvegardées de façon <strong>immédiate et sécurisée</strong> directement dans la mémoire locale de votre navigateur (<code className="font-mono bg-slate-900 px-1 py-0.5 rounded text-amber-400">localStorage</code>).
                      </p>
                      <p>
                        ✔️ <strong>Zéro connexion obligatoire</strong> : C'est ultra-rapide, ça fonctionne hors-ligne, et respecte entièrement votre vie privée. Vos objectifs restent chez vous sur cet ordinateur.
                      </p>
                      <p className="text-slate-500 italic">
                        💡 <strong>Besoin d'une synchronisation Cloud ?</strong> Si vous préférez enregistrer vos données sur des serveurs Cloud (Firebase Firestore) pour y accéder depuis votre téléphone ou un autre appareil, dites-le moi simplement et j'activerai le module de base de données Firebase Firestore !
                      </p>
                    </div>
                  </div>
                </div>
              );
            })()
          ) : (
            <div className="text-center py-10 flex flex-col items-center justify-center m-auto max-w-sm">
              <Target className="w-12 h-12 text-slate-700 mb-3" />
              <p className="text-sm text-slate-400">Sélectionnez un objectif dans la liste pour voir et gérer vos micro-tâches.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
