import React, { useState, useEffect, useRef, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, doc, getDoc, addDoc, setDoc, updateDoc, deleteDoc, onSnapshot, collection, query, where, getDocs, serverTimestamp } from 'firebase/firestore';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// --- Firebase Initialization ---
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);

// --- Global App ID ---
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

// --- Utility Functions ---
const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

const getWeekRange = (date) => {
    const startOfWeek = new Date(date);
    startOfWeek.setHours(0, 0, 0, 0);
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay()); // Sunday
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 6); // Saturday
    endOfWeek.setHours(23, 59, 59, 999);
    return { startOfWeek, endOfWeek };
};

// --- Notification Modal Component ---
const NotificationModal = ({ message, isVisible, onClose }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 text-gray-100 p-6 rounded-lg shadow-lg max-w-sm w-full border border-green-500">
                <h3 className="text-xl font-bold mb-4 text-green-400">Notification</h3>
                <p className="mb-6">{message}</p>
                <button
                    onClick={onClose}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                >
                    Dismiss
                </button>
            </div>
        </div>
    );
};

// --- Task Item Component ---
const TaskItem = ({ task, updateTask, deleteTask }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedText, setEditedText] = useState(task.text);
    const [editedPriority, setEditedPriority] = useState(task.priority);
    const [editedDueDate, setEditedDueDate] = useState(task.dueDate || '');
    const [editedReminderTime, setEditedReminderTime] = useState(task.reminderTime || '');

    const priorityColors = {
        'High': 'text-red-400',
        'Medium': 'text-yellow-400',
        'Low': 'text-blue-400',
    };

    const handleSave = () => {
        updateTask(task.id, {
            text: editedText,
            priority: editedPriority,
            dueDate: editedDueDate,
            reminderTime: editedReminderTime,
        });
        setIsEditing(false);
    };

    return (
        <div className="flex items-center justify-between bg-gray-700 p-3 rounded-md mb-2 shadow-md hover:bg-gray-600 transition-colors duration-200">
            {isEditing ? (
                <div className="flex-1 flex flex-col space-y-2">
                    <input
                        type="text"
                        value={editedText}
                        onChange={(e) => setEditedText(e.target.value)}
                        className="w-full p-2 rounded-md bg-gray-600 text-gray-100 border border-gray-500 focus:outline-none focus:border-green-500"
                    />
                    <select
                        value={editedPriority}
                        onChange={(e) => setEditedPriority(e.target.value)}
                        className="p-2 rounded-md bg-gray-600 text-gray-100 border border-gray-500 focus:outline-none focus:border-green-500"
                    >
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
                    </select>
                    <input
                        type="date"
                        value={editedDueDate}
                        onChange={(e) => setEditedDueDate(e.target.value)}
                        className="p-2 rounded-md bg-gray-600 text-gray-100 border border-gray-500 focus:outline-none focus:border-green-500"
                    />
                    <input
                        type="time"
                        value={editedReminderTime}
                        onChange={(e) => setEditedReminderTime(e.target.value)}
                        className="p-2 rounded-md bg-gray-600 text-gray-100 border border-gray-500 focus:outline-none focus:border-green-500"
                    />
                    <button
                        onClick={handleSave}
                        className="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded-md transition duration-300"
                    >
                        Save
                    </button>
                </div>
            ) : (
                <div className="flex items-center flex-1">
                    <input
                        type="checkbox"
                        checked={task.completed}
                        onChange={() => updateTask(task.id, { completed: !task.completed })}
                        className="form-checkbox h-5 w-5 text-green-500 rounded focus:ring-green-400 mr-3"
                    />
                    <span className={`flex-1 text-gray-100 ${task.completed ? 'line-through text-gray-400' : ''}`}>
                        {task.text}
                        <span className={`ml-2 text-sm ${priorityColors[task.priority] || 'text-gray-400'}`}>
                            ({task.priority})
                        </span>
                        {task.dueDate && <span className="ml-2 text-xs text-gray-400">Due: {task.dueDate}</span>}
                        {task.reminderTime && <span className="ml-2 text-xs text-gray-400">Remind: {task.reminderTime}</span>}
                    </span>
                    <div className="flex space-x-2 ml-4">
                        <button
                            onClick={() => setIsEditing(true)}
                            className="text-blue-400 hover:text-blue-300 transition-colors duration-200"
                            title="Edit Task"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                        </button>
                        <button
                            onClick={() => deleteTask(task.id)}
                            className="text-red-400 hover:text-red-300 transition-colors duration-200"
                            title="Delete Task"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

// --- To-Do List Component ---
const TodoList = ({ tasks, addTask, updateTask, deleteTask }) => {
    const [newTaskText, setNewTaskText] = useState('');
    const [newTaskPriority, setNewTaskPriority] = useState('Medium');
    const [newTaskDueDate, setNewTaskDueDate] = useState('');
    const [newTaskReminderTime, setNewTaskReminderTime] = useState('');

    const handleAddTask = () => {
        if (newTaskText.trim()) {
            addTask({
                text: newTaskText,
                priority: newTaskPriority,
                dueDate: newTaskDueDate,
                reminderTime: newTaskReminderTime,
            });
            setNewTaskText('');
            setNewTaskPriority('Medium');
            setNewTaskDueDate('');
            setNewTaskReminderTime('');
        }
    };

    return (
        <div className="p-6 bg-gray-900 rounded-lg shadow-xl h-full flex flex-col">
            <h2 className="text-3xl font-bold text-green-400 mb-6 text-center">Your To-Do List</h2>
            <div className="mb-6 p-4 bg-gray-800 rounded-md shadow-inner">
                <input
                    type="text"
                    placeholder="Add a new task..."
                    value={newTaskText}
                    onChange={(e) => setNewTaskText(e.target.value)}
                    className="w-full p-3 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500 mb-3"
                />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
                    <select
                        value={newTaskPriority}
                        onChange={(e) => setNewTaskPriority(e.target.value)}
                        className="p-3 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500"
                    >
                        <option value="Low">Low Priority</option>
                        <option value="Medium">Medium Priority</option>
                        <option value="High">High Priority</option>
                    </select>
                    <input
                        type="date"
                        value={newTaskDueDate}
                        onChange={(e) => setNewTaskDueDate(e.target.value)}
                        className="p-3 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500"
                        title="Due Date"
                    />
                    <input
                        type="time"
                        value={newTaskReminderTime}
                        onChange={(e) => setNewTaskReminderTime(e.target.value)}
                        className="p-3 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500"
                        title="Reminder Time"
                    />
                </div>
                <button
                    onClick={handleAddTask}
                    className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                >
                    Add Task
                </button>
            </div>
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {tasks
                    .sort((a, b) => {
                        const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
                        return priorityOrder[b.priority] - priorityOrder[a.priority];
                    })
                    .map((task) => (
                        <TaskItem
                            key={task.id}
                            task={task}
                            updateTask={updateTask}
                            deleteTask={deleteTask}
                        />
                    ))}
                {tasks.length === 0 && (
                    <p className="text-gray-400 text-center mt-8">No tasks yet! Add some to get started.</p>
                )}
            </div>
        </div>
    );
};

// --- Pomodoro Timer Component ---
const PomodoroTimer = ({ onPomodoroComplete }) => {
    const [minutes, setMinutes] = useState(25);
    const [seconds, setSeconds] = useState(0);
    const [isActive, setIsActive] = useState(false);
    const [mode, setMode] = useState('work'); // 'work' or 'break'
    const [workDuration, setWorkDuration] = useState(25);
    const [breakDuration, setBreakDuration] = useState(5);

    const timerRef = useRef(null);

    const toggle = () => {
        setIsActive(!isActive);
    };

    const reset = () => {
        setIsActive(false);
        setMode('work');
        setMinutes(workDuration);
        setSeconds(0);
        clearInterval(timerRef.current);
    };

    const switchMode = useCallback(() => {
        if (mode === 'work') {
            onPomodoroComplete(workDuration, 'work');
            setMode('break');
            setMinutes(breakDuration);
        } else {
            onPomodoroComplete(breakDuration, 'break');
            setMode('work');
            setMinutes(workDuration);
        }
        setSeconds(0);
        setIsActive(false); // Pause after mode switch
    }, [mode, workDuration, breakDuration, onPomodoroComplete]);

    useEffect(() => {
        if (isActive) {
            timerRef.current = setInterval(() => {
                if (seconds === 0) {
                    if (minutes === 0) {
                        clearInterval(timerRef.current);
                        switchMode();
                    } else {
                        setMinutes(minutes - 1);
                        setSeconds(59);
                    }
                } else {
                    setSeconds(seconds - 1);
                }
            }, 1000);
        } else {
            clearInterval(timerRef.current);
        }

        return () => clearInterval(timerRef.current);
    }, [isActive, minutes, seconds, switchMode]);

    useEffect(() => {
        if (mode === 'work') {
            setMinutes(workDuration);
        } else {
            setMinutes(breakDuration);
        }
        setSeconds(0);
    }, [mode, workDuration, breakDuration]);

    return (
        <div className="p-6 bg-gray-900 rounded-lg shadow-xl text-center h-full flex flex-col justify-center items-center">
            <h2 className="text-3xl font-bold text-green-400 mb-6">Pomodoro Timer</h2>
            <div className="flex justify-center mb-4 space-x-4">
                <button
                    onClick={() => { setMode('work'); setIsActive(false); }}
                    className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${mode === 'work' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                >
                    Work ({workDuration} min)
                </button>
                <button
                    onClick={() => { setMode('break'); setIsActive(false); }}
                    className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${mode === 'break' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                >
                    Break ({breakDuration} min)
                </button>
            </div>
            <div className="text-7xl font-mono text-white mb-8 bg-gray-800 p-6 rounded-xl shadow-inner border-2 border-gray-700">
                {formatTime(minutes * 60 + seconds)}
            </div>
            <div className="flex space-x-4 mb-6">
                <button
                    onClick={toggle}
                    className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                >
                    {isActive ? 'Pause' : 'Start'}
                </button>
                <button
                    onClick={reset}
                    className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                >
                    Reset
                </button>
                <button
                    onClick={switchMode}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-6 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                >
                    Skip
                </button>
            </div>
            <div className="flex flex-col space-y-2 text-gray-300">
                <label className="flex items-center space-x-2">
                    Work Duration (minutes):
                    <input
                        type="number"
                        value={workDuration}
                        onChange={(e) => setWorkDuration(Math.max(1, parseInt(e.target.value) || 25))}
                        className="w-20 p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500"
                    />
                </label>
                <label className="flex items-center space-x-2">
                    Break Duration (minutes):
                    <input
                        type="number"
                        value={breakDuration}
                        onChange={(e) => setBreakDuration(Math.max(1, parseInt(e.target.value) || 5))}
                        className="w-20 p-2 rounded-md bg-gray-700 text-gray-100 border border-gray-600 focus:outline-none focus:border-green-500"
                    />
                </label>
            </div>
        </div>
    );
};

// --- Weekly Analysis Component ---
const WeeklyAnalysis = ({ tasks, pomodoroHistory }) => {
    const today = new Date();
    const { startOfWeek, endOfWeek } = getWeekRange(today);

    // Filter data for the current week
    const weeklyTasks = tasks.filter(task => {
        if (!task.completedAt) return false;
        const completedDate = new Date(task.completedAt.toDate());
        return completedDate >= startOfWeek && completedDate <= endOfWeek;
    });

    const weeklyPomodoros = pomodoroHistory.filter(session => {
        const sessionDate = new Date(session.startTime.toDate());
        return sessionDate >= startOfWeek && sessionDate <= endOfWeek;
    });

    // Prepare data for tasks completed per day
    const tasksPerDay = {};
    for (let i = 0; i < 7; i++) {
        const d = new Date(startOfWeek);
        d.setDate(startOfWeek.getDate() + i);
        tasksPerDay[d.toLocaleDateString('en-US', { weekday: 'short' })] = 0;
    }
    weeklyTasks.forEach(task => {
        const day = new Date(task.completedAt.toDate()).toLocaleDateString('en-US', { weekday: 'short' });
        tasksPerDay[day]++;
    });
    const tasksChartData = Object.keys(tasksPerDay).map(day => ({
        name: day,
        tasks: tasksPerDay[day]
    }));

    // Prepare data for pomodoro sessions per type
    const pomodoroTypeData = { work: 0, break: 0 };
    weeklyPomodoros.forEach(session => {
        pomodoroTypeData[session.type] += session.duration;
    });
    const pomodoroChartData = [
        { name: 'Work', value: pomodoroTypeData.work, color: '#4CAF50' },
        { name: 'Break', value: pomodoroTypeData.break, color: '#2196F3' },
    ];

    // Prepare data for task priority distribution
    const priorityDistribution = { 'High': 0, 'Medium': 0, 'Low': 0 };
    weeklyTasks.forEach(task => {
        priorityDistribution[task.priority]++;
    });
    const priorityChartData = [
        { name: 'High', value: priorityDistribution.High, color: '#EF4444' },
        { name: 'Medium', value: priorityDistribution.Medium, color: '#F59E0B' },
        { name: 'Low', value: priorityDistribution.Low, color: '#3B82F6' },
    ];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']; // For general pie chart

    return (
        <div className="p-6 bg-gray-900 rounded-lg shadow-xl h-full flex flex-col overflow-y-auto custom-scrollbar">
            <h2 className="text-3xl font-bold text-green-400 mb-6 text-center">Weekly Analysis</h2>
            <p className="text-gray-300 text-center mb-6">
                Insights for the week: {startOfWeek.toLocaleDateString()} - {endOfWeek.toLocaleDateString()}
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-grow">
                <div className="bg-gray-800 p-4 rounded-md shadow-inner">
                    <h3 className="text-xl font-semibold text-gray-100 mb-4">Tasks Completed Per Day</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={tasksChartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                            <XAxis dataKey="name" stroke="#9CA3AF" />
                            <YAxis stroke="#9CA3AF" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563', borderRadius: '4px' }}
                                itemStyle={{ color: '#E5E7EB' }}
                            />
                            <Legend />
                            <Bar dataKey="tasks" fill="#10B981" name="Tasks Completed" radius={[5, 5, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="bg-gray-800 p-4 rounded-md shadow-inner">
                    <h3 className="text-xl font-semibold text-gray-100 mb-4">Pomodoro Time Distribution (Minutes)</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={pomodoroChartData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                                nameKey="name"
                            >
                                {pomodoroChartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563', borderRadius: '4px' }}
                                itemStyle={{ color: '#E5E7EB' }}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                <div className="bg-gray-800 p-4 rounded-md shadow-inner lg:col-span-2">
                    <h3 className="text-xl font-semibold text-gray-100 mb-4">Task Priority Distribution</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={priorityChartData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                                nameKey="name"
                            >
                                {priorityChartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563', borderRadius: '4px' }}
                                itemStyle={{ color: '#E5E7EB' }}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

// --- Reward System Component ---
const RewardSystem = ({ rewards, updateRewards }) => {
    const rewardTiers = [
        { id: 'snake-skin-1', name: 'Green Snake Skin', cost: 10, type: 'cosmetic', value: 'green' },
        { id: 'snake-skin-2', name: 'Blue Snake Skin', cost: 25, type: 'cosmetic', value: 'blue' },
        { id: 'background-1', name: 'GitHub Grid Background', cost: 50, type: 'cosmetic', value: 'grid' },
        { id: 'speed-boost', name: 'Permanent Speed Boost', cost: 100, type: 'game_modifier', value: 0.8 }, // Multiplier for speed
    ];

    const handleUnlockReward = (reward) => {
        if (rewards.points >= reward.cost && !rewards.unlockedItems.includes(reward.id)) {
            const newPoints = rewards.points - reward.cost;
            const newUnlockedItems = [...rewards.unlockedItems, reward.id];
            updateRewards(newPoints, newUnlockedItems);
        } else if (rewards.unlockedItems.includes(reward.id)) {
            // Already unlocked
        } else {
            // Not enough points
        }
    };

    return (
        <div className="p-6 bg-gray-900 rounded-lg shadow-xl h-full flex flex-col overflow-y-auto custom-scrollbar">
            <h2 className="text-3xl font-bold text-green-400 mb-6 text-center">Reward System</h2>
            <div className="bg-gray-800 p-4 rounded-md mb-6 text-center shadow-inner">
                <p className="text-gray-100 text-xl font-semibold">Current Stars: <span className="text-yellow-400">{rewards.points} ⭐</span></p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-grow">
                {rewardTiers.map(reward => (
                    <div key={reward.id} className="bg-gray-800 p-4 rounded-md shadow-md flex flex-col items-center text-center">
                        <h3 className="text-xl font-semibold text-gray-100 mb-2">{reward.name}</h3>
                        <p className="text-gray-300 mb-4">{reward.type === 'cosmetic' ? 'Visual customization' : 'Game advantage'}</p>
                        <p className="text-yellow-400 text-lg font-bold mb-4">{reward.cost} ⭐</p>
                        <button
                            onClick={() => handleUnlockReward(reward)}
                            disabled={rewards.points < reward.cost || rewards.unlockedItems.includes(reward.id)}
                            className={`w-full py-2 px-4 rounded-md font-bold transition duration-300 ease-in-out transform hover:scale-105
                                ${rewards.unlockedItems.includes(reward.id)
                                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                                    : rewards.points >= reward.cost
                                        ? 'bg-green-600 hover:bg-green-700 text-white'
                                        : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                }`}
                        >
                            {rewards.unlockedItems.includes(reward.id) ? 'Unlocked!' : 'Unlock'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};


// --- Game Component ---
const Game = ({ rewards, onGameOver, onAppleEat }) => {
    const canvasRef = useRef(null);
    const [score, setScore] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [gameStarted, setGameStarted] = useState(false);
    const [highScore, setHighScore] = useState(0);

    const snakeSpeedMultiplier = rewards.unlockedItems.includes('speed-boost') ? 0.8 : 1; // Example speed boost

    const GRID_SIZE = 20;
    const INITIAL_SNAKE_SPEED = 100 * snakeSpeedMultiplier; // Milliseconds per frame

    const [snake, setSnake] = useState([{ x: 10, y: 10 }]);
    const [apple, setApple] = useState({ x: 15, y: 10 });
    const [direction, setDirection] = useState({ x: 1, y: 0 }); // Initial direction: right
    const [changingDirection, setChangingDirection] = useState(false); // To prevent multiple direction changes per frame

    const gameLoopRef = useRef(null);
    const lastRenderTimeRef = useRef(0);

    const generateApple = useCallback((currentSnake) => {
        let newApple;
        let collision;
        do {
            newApple = {
                x: Math.floor(Math.random() * (canvasRef.current.width / GRID_SIZE)),
                y: Math.floor(Math.random() * (canvasRef.current.height / GRID_SIZE)),
            };
            collision = currentSnake.some(segment => segment.x === newApple.x && segment.y === newApple.y);
        } while (collision);
        setApple(newApple);
    }, []);

    const draw = useCallback((ctx, snakeSegments, currentApple) => {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height); // Clear canvas

        // Apply background cosmetic
        if (rewards.unlockedItems.includes('background-1')) {
            // Simple grid pattern
            ctx.strokeStyle = '#374151'; // Gray-700
            for (let x = 0; x < ctx.canvas.width; x += GRID_SIZE) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, ctx.canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < ctx.canvas.height; y += GRID_SIZE) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(ctx.canvas.width, y);
                ctx.stroke();
            }
        }

        // Draw snake
        const snakeColor = rewards.unlockedItems.includes('snake-skin-2') ? '#3B82F6' : (rewards.unlockedItems.includes('snake-skin-1') ? '#10B981' : '#22C55E'); // Blue, Green, Default Green
        snakeSegments.forEach(segment => {
            ctx.fillStyle = snakeColor;
            ctx.strokeStyle = '#1F2937'; // Dark gray for border
            ctx.fillRect(segment.x * GRID_SIZE, segment.y * GRID_SIZE, GRID_SIZE, GRID_SIZE);
            ctx.strokeRect(segment.x * GRID_SIZE, segment.y * GRID_SIZE, GRID_SIZE, GRID_SIZE);
        });

        // Draw apple (star icon)
        ctx.fillStyle = '#FBBF24'; // Amber-400
        const appleX = currentApple.x * GRID_SIZE + GRID_SIZE / 2;
        const appleY = currentApple.y * GRID_SIZE + GRID_SIZE / 2;
        const outerRadius = GRID_SIZE * 0.4;
        const innerRadius = GRID_SIZE * 0.15;
        const numPoints = 5;

        ctx.beginPath();
        for (let i = 0; i < numPoints * 2; i++) {
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const angle = (Math.PI / numPoints) * i;
            const x = appleX + radius * Math.sin(angle);
            const y = appleY - radius * Math.cos(angle);
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#D97706'; // Amber-700
        ctx.stroke();

    }, [rewards.unlockedItems]);

    const updateGame = useCallback(() => {
        if (gameOver || !gameStarted) return;

        setChangingDirection(false);

        setSnake(prevSnake => {
            const newSnake = [...prevSnake];
            const head = { x: newSnake[0].x + direction.x, y: newSnake[0].y + direction.y };

            // Check for wall collision
            const canvas = canvasRef.current;
            if (head.x < 0 || head.x >= canvas.width / GRID_SIZE ||
                head.y < 0 || head.y >= canvas.height / GRID_SIZE) {
                setGameOver(true);
                onGameOver(score);
                return prevSnake;
            }

            // Check for self-collision
            for (let i = 1; i < newSnake.length; i++) {
                if (head.x === newSnake[i].x && head.y === newSnake[i].y) {
                    setGameOver(true);
                    onGameOver(score);
                    return prevSnake;
                }
            }

            newSnake.unshift(head); // Add new head

            // Check for apple collision
            if (head.x === apple.x && head.y === apple.y) {
                setScore(prevScore => prevScore + 1);
                onAppleEat(); // Notify App.js to update rewards
                generateApple(newSnake); // Generate new apple
            } else {
                newSnake.pop(); // Remove tail if no apple eaten
            }

            return newSnake;
        });
    }, [gameOver, gameStarted, direction, apple, score, onGameOver, onAppleEat, generateApple]);

    const gameLoop = useCallback((currentTime) => {
        if (gameOver || !gameStarted) {
            cancelAnimationFrame(gameLoopRef.current);
            return;
        }

        const elapsed = currentTime - lastRenderTimeRef.current;
        if (elapsed > INITIAL_SNAKE_SPEED) {
            lastRenderTimeRef.current = currentTime - (elapsed % INITIAL_SNAKE_SPEED);
            updateGame();
        }

        const ctx = canvasRef.current.getContext('2d');
        draw(ctx, snake, apple);

        gameLoopRef.current = requestAnimationFrame(gameLoop);
    }, [gameOver, gameStarted, updateGame, snake, apple, draw]);

    const handleKeyDown = useCallback((e) => {
        if (changingDirection) return;

        const keyPressed = e.key;
        const goingUp = direction.y === -1;
        const goingDown = direction.y === 1;
        const goingLeft = direction.x === -1;
        const goingRight = direction.x === 1;

        if (keyPressed === 'ArrowLeft' && !goingRight) {
            setDirection({ x: -1, y: 0 });
            setChangingDirection(true);
        } else if (keyPressed === 'ArrowUp' && !goingDown) {
            setDirection({ x: 0, y: -1 });
            setChangingDirection(true);
        } else if (keyPressed === 'ArrowRight' && !goingLeft) {
            setDirection({ x: 1, y: 0 });
            setChangingDirection(true);
        } else if (keyPressed === 'ArrowDown' && !goingUp) {
            setDirection({ x: 0, y: 1 });
            setChangingDirection(true);
        }
    }, [changingDirection, direction]);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // Set canvas dimensions dynamically
        const parent = canvas.parentElement;
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;

        const resizeCanvas = () => {
            canvas.width = parent.clientWidth;
            canvas.height = parent.clientHeight;
            if (gameStarted && !gameOver) {
                draw(ctx, snake, apple); // Redraw on resize
            }
        };

        window.addEventListener('resize', resizeCanvas);
        document.addEventListener('keydown', handleKeyDown);

        if (gameStarted && !gameOver) {
            gameLoopRef.current = requestAnimationFrame(gameLoop);
        }

        return () => {
            window.removeEventListener('resize', resizeCanvas);
            document.removeEventListener('keydown', handleKeyDown);
            cancelAnimationFrame(gameLoopRef.current);
        };
    }, [gameStarted, gameOver, gameLoop, handleKeyDown, draw, snake, apple]);

    const startGame = () => {
        setSnake([{ x: 10, y: 10 }]);
        generateApple([{ x: 10, y: 10 }]);
        setDirection({ x: 1, y: 0 });
        setScore(0);
        setGameOver(false);
        setGameStarted(true);
        lastRenderTimeRef.current = performance.now(); // Reset timer for game loop
        gameLoopRef.current = requestAnimationFrame(gameLoop);
    };

    // Load high score from local storage on mount
    useEffect(() => {
        const storedHighScore = localStorage.getItem('snakeHighScore');
        if (storedHighScore) {
            setHighScore(parseInt(storedHighScore, 10));
        }
    }, []);

    // Update high score in local storage when game ends
    useEffect(() => {
        if (gameOver && score > highScore) {
            setHighScore(score);
            localStorage.setItem('snakeHighScore', score.toString());
        }
    }, [gameOver, score, highScore]);


    return (
        <div className="flex flex-col items-center justify-center bg-gray-900 rounded-lg shadow-xl h-full p-4">
            <h2 className="text-3xl font-bold text-green-400 mb-4">GitHub Snake</h2>
            <div className="flex justify-between w-full max-w-md mb-4 px-4">
                <p className="text-gray-100 text-xl">Score: <span className="font-bold">{score}</span></p>
                <p className="text-gray-100 text-xl">High Score: <span className="font-bold">{highScore}</span></p>
            </div>
            <div className="w-full h-full max-w-xl max-h-xl bg-gray-800 rounded-md overflow-hidden border-2 border-gray-700">
                <canvas
                    ref={canvasRef}
                    className="w-full h-full"
                    style={{ aspectRatio: '1 / 1' }} // Maintain aspect ratio
                ></canvas>
            </div>
            <div className="mt-6">
                {!gameStarted && (
                    <button
                        onClick={startGame}
                        className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                    >
                        Start Game
                    </button>
                )}
                {gameOver && (
                    <div className="text-center">
                        <p className="text-red-500 text-2xl font-bold mb-4">Game Over!</p>
                        <button
                            onClick={startGame}
                            className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-md transition duration-300 ease-in-out transform hover:scale-105"
                        >
                            Play Again
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};


// --- Main App Component ---
export default function App() {
    const [userId, setUserId] = useState(null);
    const [isAuthReady, setIsAuthReady] = useState(false);
    const [tasks, setTasks] = useState([]);
    const [pomodoroHistory, setPomodoroHistory] = useState([]);
    const [rewards, setRewards] = useState({ points: 0, unlockedItems: [] });
    const [currentView, setCurrentView] = useState('todo'); // 'todo', 'pomodoro', 'game', 'analysis', 'rewards'

    const [notificationMessage, setNotificationMessage] = useState('');
    const [showNotificationModal, setShowNotificationModal] = useState(false);

    // Firebase Authentication and Data Listeners
    useEffect(() => {
        const authenticate = async () => {
            try {
                const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;
                if (initialAuthToken) {
                    await signInWithCustomToken(auth, initialAuthToken);
                } else {
                    await signInAnonymously(auth);
                }
            } catch (error) {
                console.error("Firebase authentication error:", error);
                // Fallback to anonymous sign-in if custom token fails
                try {
                    await signInAnonymously(auth);
                } catch (anonError) {
                    console.error("Anonymous sign-in failed:", anonError);
                }
            }
        };

        authenticate();

        const unsubscribeAuth = onAuthStateChanged(auth, (user) => {
            if (user) {
                setUserId(user.uid);
                setIsAuthReady(true);
            } else {
                setUserId(crypto.randomUUID()); // Use random UUID for unauthenticated users
                setIsAuthReady(true);
            }
        });

        return () => unsubscribeAuth();
    }, []);

    // Firestore Data Listeners
    useEffect(() => {
        if (!isAuthReady || !userId) return;

        // Tasks Listener
        const tasksCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/tasks`);
        const unsubscribeTasks = onSnapshot(tasksCollectionRef, (snapshot) => {
            const fetchedTasks = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data(),
                // Convert Firestore Timestamp to Date object if it exists
                createdAt: doc.data().createdAt?.toDate(),
                completedAt: doc.data().completedAt?.toDate(),
            }));
            setTasks(fetchedTasks);
        }, (error) => console.error("Error fetching tasks:", error));

        // Pomodoro History Listener
        const pomodoroCollectionRef = collection(db, `artifacts/${appId}/users/${userId}/pomodoroSessions`);
        const unsubscribePomodoros = onSnapshot(pomodoroCollectionRef, (snapshot) => {
            const fetchedSessions = snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data(),
                startTime: doc.data().startTime?.toDate(),
                endTime: doc.data().endTime?.toDate(),
            }));
            setPomodoroHistory(fetchedSessions);
        }, (error) => console.error("Error fetching pomodoro history:", error));

        // Rewards Listener
        const rewardsDocRef = doc(db, `artifacts/${appId}/users/${userId}/rewards/userRewards`);
        const unsubscribeRewards = onSnapshot(rewardsDocRef, (docSnap) => {
            if (docSnap.exists()) {
                setRewards(docSnap.data());
            } else {
                // Initialize rewards if they don't exist
                setDoc(rewardsDocRef, { points: 0, unlockedItems: [] });
            }
        }, (error) => console.error("Error fetching rewards:", error));


        return () => {
            unsubscribeTasks();
            unsubscribePomodoros();
            unsubscribeRewards();
        };
    }, [isAuthReady, userId]); // Re-run when auth state is ready or userId changes

    // --- Task Management Functions ---
    const addTask = async (newTask) => {
        if (!userId) return;
        try {
            await addDoc(collection(db, `artifacts/${appId}/users/${userId}/tasks`), {
                ...newTask,
                completed: false,
                createdAt: serverTimestamp(),
            });
        } catch (e) {
            console.error("Error adding document: ", e);
        }
    };

    const updateTask = async (id, updates) => {
        if (!userId) return;
        try {
            const taskDocRef = doc(db, `artifacts/${appId}/users/${userId}/tasks`, id);
            if (updates.completed) {
                // If marking as complete, add reward points
                const currentTask = tasks.find(t => t.id === id);
                if (currentTask && !currentTask.completed) { // Only reward if it's being marked complete now
                    const pointsEarned = { 'Low': 1, 'Medium': 3, 'High': 5 }[currentTask.priority] || 1;
                    updateRewards(rewards.points + pointsEarned, rewards.unlockedItems);
                }
                await updateDoc(taskDocRef, { ...updates, completedAt: serverTimestamp() });
            } else {
                // If unmarking complete, remove completedAt timestamp
                await updateDoc(taskDocRef, { ...updates, completedAt: null });
            }
        } catch (e) {
            console.error("Error updating document: ", e);
        }
    };

    const deleteTask = async (id) => {
        if (!userId) return;
        try {
            await deleteDoc(doc(db, `artifacts/${appId}/users/${userId}/tasks`, id));
        } catch (e) {
            console.error("Error deleting document: ", e);
        }
    };

    // --- Pomodoro Management Functions ---
    const addPomodoroSession = async (duration, type) => {
        if (!userId) return;
        try {
            await addDoc(collection(db, `artifacts/${appId}/users/${userId}/pomodoroSessions`), {
                duration,
                type,
                startTime: serverTimestamp(),
                endTime: serverTimestamp(), // For simplicity, end time is same as start for now
            });
        } catch (e) {
            console.error("Error adding pomodoro session: ", e);
        }
    };

    // --- Reward Management Functions ---
    const updateRewards = async (newPoints, newUnlockedItems) => {
        if (!userId) return;
        try {
            const rewardsDocRef = doc(db, `artifacts/${appId}/users/${userId}/rewards/userRewards`);
            await setDoc(rewardsDocRef, { points: newPoints, unlockedItems: newUnlockedItems }, { merge: true });
        } catch (e) {
            console.error("Error updating rewards: ", e);
        }
    };

    // --- Game Over Handler ---
    const handleGameOver = (finalScore) => {
        // Potentially add more rewards based on game score here
        // For now, task completion is the primary reward source
        console.log("Game Over! Score:", finalScore);
    };

    // --- Apple Eat Handler (for game rewards) ---
    const handleAppleEat = () => {
        // Award a small amount of points for eating an apple in game
        updateRewards(rewards.points + 1, rewards.unlockedItems);
    };

    // --- Reminder Logic ---
    useEffect(() => {
        if (!isAuthReady || !userId) return;

        const interval = setInterval(() => {
            const now = new Date();
            const currentTime = now.getHours() * 60 + now.getMinutes(); // Minutes since midnight
            const today = now.toISOString().split('T')[0]; // YYYY-MM-DD

            tasks.forEach(task => {
                if (!task.completed && task.dueDate === today && task.reminderTime) {
                    const [reminderHours, reminderMinutes] = task.reminderTime.split(':').map(Number);
                    const reminderTimeInMinutes = reminderHours * 60 + reminderMinutes;

                    // Trigger reminder if time is within the last minute and not already shown
                    if (currentTime === reminderTimeInMinutes &&
                        !sessionStorage.getItem(`reminder-${task.id}-${today}`)) {
                        setNotificationMessage(`Reminder: Don't forget "${task.text}"!`);
                        setShowNotificationModal(true);
                        sessionStorage.setItem(`reminder-${task.id}-${today}`, 'true'); // Mark as shown for today
                        // Optional: Browser notification
                        if (Notification.permission === 'granted') {
                            new Notification('Task Reminder', {
                                body: `Don't forget "${task.text}"!`,
                                icon: 'https://placehold.co/64x64/000000/FFFFFF?text=🔔'
                            });
                        } else if (Notification.permission !== 'denied') {
                            Notification.requestPermission().then(permission => {
                                if (permission === 'granted') {
                                    new Notification('Task Reminder', {
                                        body: `Don't forget "${task.text}"!`,
                                        icon: 'https://placehold.co/64x64/000000/FFFFFF?text=🔔'
                                    });
                                }
                            });
                        }
                    }
                }
            });
        }, 60 * 1000); // Check every minute

        return () => clearInterval(interval);
    }, [tasks, isAuthReady, userId]);


    if (!isAuthReady) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-950 text-green-400 text-2xl">
                Loading Application...
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 font-inter flex flex-col">
            <style>
                {`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
                body { font-family: 'Inter', sans-serif; }
                .custom-scrollbar::-webkit-scrollbar {
                    width: 8px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: #1F2937; /* Dark gray */
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: #059669; /* Green-600 */
                    border-radius: 10px;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #047857; /* Green-700 */
                }
                `}
            </style>
            <NotificationModal
                message={notificationMessage}
                isVisible={showNotificationModal}
                onClose={() => setShowNotificationModal(false)}
            />
            <header className="bg-gray-800 p-4 shadow-lg flex flex-col sm:flex-row justify-between items-center">
                <h1 className="text-4xl font-bold text-green-400 mb-2 sm:mb-0">
                    GitHub Productivity Game
                </h1>
                <nav className="flex space-x-4">
                    <button
                        onClick={() => setCurrentView('todo')}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${currentView === 'todo' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                        To-Do List
                    </button>
                    <button
                        onClick={() => setCurrentView('pomodoro')}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${currentView === 'pomodoro' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                        Pomodoro
                    </button>
                    <button
                        onClick={() => setCurrentView('game')}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${currentView === 'game' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                        Game
                    </button>
                    <button
                        onClick={() => setCurrentView('analysis')}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${currentView === 'analysis' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                        Analysis
                    </button>
                    <button
                        onClick={() => setCurrentView('rewards')}
                        className={`px-4 py-2 rounded-md font-semibold transition-colors duration-200 ${currentView === 'rewards' ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                    >
                        Rewards
                    </button>
                </nav>
            </header>

            <main className="flex-1 p-6 flex items-stretch justify-center">
                <div className="w-full max-w-4xl h-[calc(100vh-160px)]"> {/* Adjusted height to fit viewport */}
                    {currentView === 'todo' && (
                        <TodoList tasks={tasks} addTask={addTask} updateTask={updateTask} deleteTask={deleteTask} />
                    )}
                    {currentView === 'pomodoro' && (
                        <PomodoroTimer onPomodoroComplete={addPomodoroSession} />
                    )}
                    {currentView === 'game' && (
                        <Game rewards={rewards} onGameOver={handleGameOver} onAppleEat={handleAppleEat} />
                    )}
                    {currentView === 'analysis' && (
                        <WeeklyAnalysis tasks={tasks} pomodoroHistory={pomodoroHistory} />
                    )}
                    {currentView === 'rewards' && (
                        <RewardSystem rewards={rewards} updateRewards={updateRewards} />
                    )}
                </div>
            </main>

            <footer className="bg-gray-800 p-3 text-center text-gray-400 text-sm shadow-inner">
                <p>Logged in as User ID: <span className="font-mono text-green-300">{userId || 'N/A'}</span></p>
                <p>&copy; 2023 GitHub Productivity Game. All rights reserved.</p>
            </footer>
        </div>
    );
}
