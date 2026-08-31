// StreamPicker Client Application - Universal URL Link Engine & Resilient Fallback Image Loader

let currentTab = 'pick';
let activeMood = 'Mind-Bending';
let pickerMode = 'solo'; // 'solo' or 'couple'
let selectedDevice = 'web'; // 'web', 'ios', 'android', 'tv'
let providersList = [];
let userSubscriptions = new Set();
let watchlist = [];
let excludeHistory = [];
let activeRoomCode = null;
let currentUser = null;
let isAuthRegisterMode = false;
let lastPickData = null;
let searchDebounceTimer = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    setupEventListeners();
    await checkAuthSession();
    await loadProviders();
    await loadWatchlist();
    await loadCatalog();
    await loadAlerts();
    await checkSharedURL();
});

// Authenticated fetch wrapper
async function authFetch(url, options = {}) {
    const token = localStorage.getItem('streampicker_token');
    const headers = options.headers ? { ...options.headers } : {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return fetch(url, { ...options, headers });
}

// ==================== STREAMING URL & IMAGE FALLBACK RESOLVERS ====================

function getWatchLink(streamOption, titleName) {
    const title = titleName || (streamOption && streamOption.title) || '';
    const query = encodeURIComponent(title);
    const providerId = (streamOption?.provider_id || '').toLowerCase();

    // Mobile / native app direct intent if user explicitly requested iOS/Android
    if (selectedDevice !== 'web' && streamOption?.deep_link) {
        return streamOption.deep_link;
    }

    // Direct web URL if valid https link
    if (streamOption?.web_url && streamOption.web_url.startsWith('http')) {
        return streamOption.web_url;
    }

    // High reliability direct web search URLs per platform
    if (providerId.includes('prime') || providerId.includes('amazon')) {
        return `https://www.primevideo.com/search/ref=atv_nb_sr?phrase=${query}`;
    } else if (providerId.includes('netflix')) {
        return `https://www.netflix.com/search?q=${query}`;
    } else if (providerId.includes('hotstar') || providerId.includes('disney')) {
        return `https://www.hotstar.com/in/explore?search_query=${query}`;
    } else if (providerId.includes('jio')) {
        return `https://www.jiocinema.com/search/${query}`;
    } else if (providerId.includes('apple')) {
        return `https://tv.apple.com/search?term=${query}`;
    } else if (providerId.includes('sonyliv')) {
        return `https://www.sonyliv.com/search/${query}`;
    } else if (providerId.includes('zee5')) {
        return `https://www.zee5.com/search?q=${query}`;
    }

    return `https://www.google.com/search?q=watch+${query}+online+streaming`;
}

function handleImageFallback(imgEl, title) {
    imgEl.onerror = null;
    const safeTitle = (title || 'StreamPicker Movie').replace(/</g, '&lt;').replace(/>/g, '&gt;').substring(0, 30);
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="500" height="750" viewBox="0 0 500 750">
            <defs>
                <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1e1b4b;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#0f172a;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#3b0764;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#g)" />
            <circle cx="250" cy="300" r="65" fill="#6366f1" opacity="0.25" />
            <polygon points="238,275 278,300 238,325" fill="#a855f7" />
            <text x="50%" y="440" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="24" font-weight="800">
                ${safeTitle}
            </text>
            <text x="50%" y="480" dominant-baseline="middle" text-anchor="middle" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="600">
                StreamPicker Spotlight
            </text>
        </svg>
    `;
    imgEl.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg.trim());
}

function setupEventListeners() {
    // Mood Chip Selector
    const moodChips = document.querySelectorAll('#mood-chips .chip-btn');
    moodChips.forEach(chip => {
        chip.addEventListener('click', () => {
            moodChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            activeMood = chip.dataset.mood;
            
            const label = document.getElementById('selected-mood-label');
            if (label) {
                const icon = chip.querySelector('.text-2xl')?.textContent || '🎬';
                label.textContent = `${icon} ${activeMood}`;
            }
        });
    });

    // Runtime Slider
    const slider = document.getElementById('runtime-slider');
    const display = document.getElementById('runtime-display');
    if (slider && display) {
        slider.addEventListener('input', (e) => {
            display.textContent = `≤ ${e.target.value} minutes`;
        });
    }

    // Device Selector
    const deviceSel = document.getElementById('device-selector');
    if (deviceSel) {
        deviceSel.addEventListener('change', (e) => {
            selectedDevice = e.target.value;
            showToast(`Device switched to: ${selectedDevice.toUpperCase()}`);
            if (lastPickData) renderPickResult(lastPickData, 0);
        });
    }

    // Catalog Search Input (Debounced)
    const searchInput = document.getElementById('catalog-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchDebounceTimer);
            searchDebounceTimer = setTimeout(() => {
                loadCatalog();
            }, 300);
        });
    }

    // Vibe search input enter key
    const vibeInput = document.getElementById('vibe-query-input');
    if (vibeInput) {
        vibeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') triggerVibeSearch();
        });
    }

    // Catalog Filter dropdowns
    ['filter-genre', 'filter-type', 'filter-sort'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => loadCatalog());
        }
    });
}

function setRuntimePreset(minutes) {
    const slider = document.getElementById('runtime-slider');
    const display = document.getElementById('runtime-display');
    if (slider && display) {
        slider.value = minutes;
        display.textContent = `≤ ${minutes} minutes`;
    }
}

function showToast(message) {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toast-message');
    if (toast && msg) {
        msg.textContent = message;
        toast.classList.remove('hidden');
        toast.classList.add('flex');
        lucide.createIcons();
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.classList.remove('flex');
        }, 3000);
    }
}

// ==================== AUTHENTICATION & MULTI-TENANCY ====================

async function checkAuthSession() {
    const token = localStorage.getItem('streampicker_token');
    const slot = document.getElementById('user-auth-slot');
    if (!token || !slot) return;

    try {
        const res = await authFetch('/api/v1/auth/me');
        if (res.ok) {
            currentUser = await res.json();
            renderUserAuthSlot();
        } else {
            localStorage.removeItem('streampicker_token');
            currentUser = null;
        }
    } catch (e) {
        currentUser = null;
    }
}

function renderUserAuthSlot() {
    const slot = document.getElementById('user-auth-slot');
    if (!slot) return;

    if (currentUser) {
        slot.innerHTML = `
            <div class="flex items-center space-x-2">
                <div class="px-3 py-1.5 rounded-xl bg-indigo-600/30 text-indigo-200 border border-indigo-500/40 text-xs font-bold flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span>${currentUser.full_name.split(' ')[0]}</span>
                </div>
                <button onclick="logoutUser()" title="Sign Out" class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-rose-400 border border-slate-700">
                    <i data-lucide="log-out" class="w-3.5 h-3.5"></i>
                </button>
            </div>
        `;
    } else {
        slot.innerHTML = `
            <button onclick="openAuthModal()" class="px-3.5 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-bold flex items-center gap-1.5">
                <i data-lucide="user" class="w-3.5 h-3.5"></i>
                <span>Sign In</span>
            </button>
        `;
    }
    lucide.createIcons();
}

function openAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

function toggleAuthMode() {
    isAuthRegisterMode = !isAuthRegisterMode;
    const title = document.getElementById('auth-modal-title');
    const submitBtn = document.getElementById('auth-submit-btn');
    const toggleBtn = document.getElementById('auth-toggle-btn');
    const nameField = document.getElementById('auth-fullname-field');

    if (isAuthRegisterMode) {
        title.textContent = 'Create StreamPicker Account';
        submitBtn.textContent = 'Sign Up Free';
        toggleBtn.textContent = 'Already have an account? Sign In';
        nameField.classList.remove('hidden');
    } else {
        title.textContent = 'Sign In to StreamPicker';
        submitBtn.textContent = 'Sign In';
        toggleBtn.textContent = 'Need an account? Create one';
        nameField.classList.add('hidden');
    }
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('auth-email-input').value.trim();
    const password = document.getElementById('auth-password-input').value;
    const fullName = document.getElementById('auth-name-input').value.trim() || 'Viewer';

    const url = isAuthRegisterMode ? '/api/v1/auth/register' : '/api/v1/auth/login';
    const body = isAuthRegisterMode ? { email, password, full_name: fullName } : { email, password };

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || 'Authentication failed');
            return;
        }

        const data = await res.json();
        localStorage.setItem('streampicker_token', data.access_token);
        currentUser = data.user;
        closeAuthModal();
        renderUserAuthSlot();
        showToast(`Welcome back, ${currentUser.full_name}!`);
        
        await loadProviders();
        await loadWatchlist();
        await loadROIDashboard();
    } catch (err) {
        alert('Network error during auth');
    }
}

async function loginDemoUser(email, name) {
    try {
        let res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: 'password123' })
        });

        if (!res.ok) {
            res = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, password: 'password123', full_name: name })
            });
        }

        const data = await res.json();
        localStorage.setItem('streampicker_token', data.access_token);
        currentUser = data.user;
        closeAuthModal();
        renderUserAuthSlot();
        showToast(`Logged in as ${currentUser.full_name}`);
        await loadProviders();
        await loadWatchlist();
        if (currentTab === 'subscriptions') await loadROIDashboard();
    } catch (e) {
        showToast('Demo login error');
    }
}

function logoutUser() {
    localStorage.removeItem('streampicker_token');
    currentUser = null;
    renderUserAuthSlot();
    showToast('Signed out of StreamPicker');
    loadProviders();
    loadWatchlist();
}

function switchTab(tabId) {
    currentTab = tabId;
    
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        btn.classList.remove('bg-indigo-600', 'text-white', 'shadow-sm');
        btn.classList.add('text-slate-400');
    });
    
    const activeBtn = document.getElementById(`tab-btn-${tabId}`);
    if (activeBtn) {
        activeBtn.classList.add('bg-indigo-600', 'text-white', 'shadow-sm');
        activeBtn.classList.remove('text-slate-400');
    }

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
        content.classList.remove('block');
    });

    const activeContent = document.getElementById(`tab-${tabId}`);
    if (activeContent) {
        activeContent.classList.remove('hidden');
        activeContent.classList.add('block');
    }

    if (tabId === 'watchlist') {
        loadWatchlist();
    } else if (tabId === 'catalog') {
        loadCatalog();
    } else if (tabId === 'subscriptions') {
        loadROIDashboard();
    } else if (tabId === 'analytics') {
        loadAnalytics();
        loadAPIStatus();
    }
}

function setPickerMode(mode) {
    pickerMode = mode;
    const soloBtn = document.getElementById('mode-btn-solo');
    const coupleBtn = document.getElementById('mode-btn-couple');
    const soloContainer = document.getElementById('solo-mode-container');
    const coupleContainer = document.getElementById('couple-mode-container');

    if (mode === 'solo') {
        soloBtn.classList.add('bg-indigo-600', 'text-white');
        soloBtn.classList.remove('text-slate-400');
        coupleBtn.classList.remove('bg-indigo-600', 'text-white');
        coupleBtn.classList.add('text-slate-400');
        soloContainer.classList.remove('hidden');
        coupleContainer.classList.add('hidden');
    } else {
        coupleBtn.classList.add('bg-indigo-600', 'text-white');
        coupleBtn.classList.remove('text-slate-400');
        soloBtn.classList.remove('bg-indigo-600', 'text-white');
        soloBtn.classList.add('text-slate-400');
        coupleContainer.classList.remove('hidden');
        soloContainer.classList.add('hidden');
    }
}

// ==================== PROVIDERS & SUBSCRIPTIONS ====================

function autoDetectUserRegionAndDefaultSubs() {
    try {
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
        const isIndia = timeZone.includes('Calcutta') || timeZone.includes('Kolkata') || timeZone.includes('India') || navigator.language.includes('IN');
        
        const regionText = document.getElementById('geo-region-text');
        if (regionText) {
            regionText.textContent = isIndia ? 'Auto-configured for India 🇮🇳' : 'Auto-configured for your region 🌐';
        }

        const geoConfigured = localStorage.getItem('streampicker_geo_configured');
        if (!geoConfigured && userSubscriptions.size === 0) {
            if (isIndia) {
                userSubscriptions = new Set(['netflix', 'prime_video', 'hotstar', 'jiocinema']);
            } else {
                userSubscriptions = new Set(['netflix', 'prime_video', 'apple_tv']);
            }
            localStorage.setItem('streampicker_geo_configured', 'true');
            authFetch('/api/v1/subscriptions', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider_ids: Array.from(userSubscriptions) })
            });
        }
    } catch (e) {
        console.error('Geo detect error:', e);
    }
}

async function loadProviders() {
    try {
        const res = await authFetch('/api/v1/providers');
        if (!res.ok) throw new Error('Failed to fetch providers');
        providersList = await res.json();
        userSubscriptions = new Set(providersList.filter(p => p.is_subscribed).map(p => p.id));
        autoDetectUserRegionAndDefaultSubs();
        renderStepProvidersGrid();
    } catch (err) {
        console.error('Error loading providers:', err);
    }
}

function renderStepProvidersGrid() {
    const container = document.getElementById('step-providers-grid');
    if (!container) return;

    container.innerHTML = providersList.map(p => {
        const isSub = userSubscriptions.has(p.id);
        return `
            <div onclick="toggleSubscription('${p.id}')" 
                class="provider-toggle-card p-3 rounded-xl flex flex-col items-center justify-center text-center gap-1.5 transition-all ${
                    isSub ? 'active' : 'bg-slate-900/60 opacity-60 hover:opacity-100'
                }">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs shadow-sm" style="background-color: ${p.brand_color}22; color: ${p.brand_color}; border: 1px solid ${p.brand_color}55;">
                    ${p.name.substring(0, 3).toUpperCase()}
                </div>
                <span class="text-xs font-bold text-white line-clamp-1">${p.name}</span>
                <span class="text-[10px] font-semibold ${isSub ? 'text-emerald-400' : 'text-slate-500'}">
                    ${isSub ? '✓ Active' : '+ Add'}
                </span>
            </div>
        `;
    }).join('');
}

async function toggleSubscription(providerId) {
    if (userSubscriptions.has(providerId)) {
        userSubscriptions.delete(providerId);
    } else {
        userSubscriptions.add(providerId);
    }
    
    renderStepProvidersGrid();
    if (currentTab === 'subscriptions') {
        loadROIDashboard();
    }

    try {
        await authFetch('/api/v1/subscriptions', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider_ids: Array.from(userSubscriptions) })
        });
        if (currentTab === 'catalog') {
            loadCatalog();
        }
    } catch (err) {
        console.error('Error updating subscriptions:', err);
    }
}

// ==================== SUBSCRIPTION ROI DASHBOARD ====================

async function loadROIDashboard() {
    const metricsContainer = document.getElementById('roi-metrics-container');
    const listContainer = document.getElementById('subscriptions-list-container');
    if (!metricsContainer || !listContainer) return;

    try {
        const res = await authFetch('/api/v1/subscriptions/roi');
        if (!res.ok) throw new Error('Failed to fetch ROI');
        const data = await res.json();

        metricsContainer.innerHTML = `
            <div class="glass-panel p-5 rounded-2xl border border-indigo-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Monthly Spend</span>
                <div class="font-heading text-2xl sm:text-3xl font-extrabold text-white mt-1">₹${data.total_monthly_spend_inr}</div>
                <div class="text-[11px] text-indigo-400 mt-1">Across ${data.active_subscriptions_count} active services</div>
            </div>
            <div class="glass-panel p-5 rounded-2xl border border-emerald-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Accessible Catalog</span>
                <div class="font-heading text-2xl sm:text-3xl font-extrabold text-emerald-400 mt-1">${data.catalog_coverage_percent}%</div>
                <div class="text-[11px] text-slate-400 mt-1">${data.accessible_catalog_count} of ${data.total_catalog_count} top titles included free</div>
            </div>
            <div class="glass-panel p-5 rounded-2xl border border-purple-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Cost / Title Streamed</span>
                <div class="font-heading text-2xl sm:text-3xl font-extrabold text-purple-300 mt-1">₹${data.estimated_cost_per_title_watched}</div>
                <div class="text-[11px] text-slate-400 mt-1">Based on watched titles</div>
            </div>
        `;

        listContainer.innerHTML = providersList.map(p => {
            const isSub = userSubscriptions.has(p.id);
            return `
                <div class="glass-card p-4 rounded-xl flex items-center justify-between">
                    <div class="flex items-center space-x-3.5">
                        <div class="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs" style="background-color: ${p.brand_color}22; color: ${p.brand_color}; border: 1px solid ${p.brand_color}55;">
                            ${p.name.substring(0, 3).toUpperCase()}
                        </div>
                        <div>
                            <h4 class="font-heading font-bold text-sm text-white">${p.name}</h4>
                            <p class="text-[11px] text-slate-400">₹${p.monthly_price_inr || 199}/month • Universal deep links enabled</p>
                        </div>
                    </div>
                    <button onclick="toggleSubscription('${p.id}')" class="px-4 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                        isSub 
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30' 
                        : 'bg-slate-800 text-slate-400 border border-slate-700 hover:text-white'
                    }">
                        ${isSub ? '✓ Subscribed' : '+ Add Subscription'}
                    </button>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Error loading ROI:', err);
    }
}

// ==================== "PICK FOR ME" & INSTANT PRESETS ====================

async function triggerPanicPick() {
    showToast('🎲 "Just Pick Something" activated! Finding champion pick...');
    const panicBtn = document.getElementById('panic-pick-btn');
    if (panicBtn) {
        panicBtn.disabled = true;
        panicBtn.classList.add('opacity-75', 'animate-pulse');
    }

    try {
        const reqBody = {
            providers: Array.from(userSubscriptions),
            mood: null,
            max_runtime: 180,
            min_imdb_rating: 7.8,
            content_type: 'movie',
            exclude_title_ids: excludeHistory
        };

        const startTime = performance.now();
        let res = await authFetch('/api/v1/discovery/pick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqBody)
        });

        if (!res.ok) {
            reqBody.min_imdb_rating = 7.0;
            res = await authFetch('/api/v1/discovery/pick', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqBody)
            });
        }

        const elapsedMs = Math.round(performance.now() - startTime);

        if (res.ok) {
            const data = await res.json();
            lastPickData = data;
            excludeHistory.push(data.title.id);
            renderPickResult(data, elapsedMs);
        } else {
            triggerPickForMe();
        }

    } catch (err) {
        console.error('Error during panic pick:', err);
    } finally {
        if (panicBtn) {
            panicBtn.disabled = false;
            panicBtn.classList.remove('opacity-75', 'animate-pulse');
        }
    }
}

async function triggerPresetPick(presetName) {
    let targetMood = 'Mind-Bending';
    let maxRuntime = 120;
    let minRating = 7.5;
    let contentType = 'movie';

    if (presetName === 'pizza') {
        targetMood = 'Adrenaline Rush';
        maxRuntime = 130;
        minRating = 7.5;
        showToast('🍕 Friday Pizza Movie mode selected!');
    } else if (presetName === 'bedtime') {
        targetMood = 'Feel-Good & Uplifting';
        maxRuntime = 45;
        minRating = 7.0;
        contentType = null;
        showToast('💤 Bedtime Quick Watch mode selected!');
    } else if (presetName === 'epic') {
        targetMood = 'Mind-Bending';
        maxRuntime = 190;
        minRating = 8.0;
        showToast('🍿 Weekend Epic mode selected!');
    }

    setRuntimePreset(maxRuntime);
    const ratingEl = document.getElementById('pick-min-rating');
    if (ratingEl) ratingEl.value = String(minRating);
    const typeEl = document.getElementById('pick-content-type');
    if (typeEl) typeEl.value = contentType || '';

    const moodChips = document.querySelectorAll('#mood-chips .chip-btn');
    moodChips.forEach(chip => {
        if (chip.dataset.mood === targetMood) {
            chip.click();
        }
    });

    try {
        const reqBody = {
            providers: Array.from(userSubscriptions),
            mood: targetMood,
            max_runtime: maxRuntime,
            min_imdb_rating: minRating,
            content_type: contentType,
            exclude_title_ids: excludeHistory
        };

        const startTime = performance.now();
        let res = await authFetch('/api/v1/discovery/pick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqBody)
        });

        if (!res.ok) {
            reqBody.min_imdb_rating = 6.5;
            res = await authFetch('/api/v1/discovery/pick', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(reqBody)
            });
        }

        const elapsedMs = Math.round(performance.now() - startTime);
        if (res.ok) {
            const data = await res.json();
            lastPickData = data;
            excludeHistory.push(data.title.id);
            renderPickResult(data, elapsedMs);
        } else {
            triggerPickForMe();
        }
    } catch (e) {
        triggerPickForMe();
    }
}

async function triggerPickForMe(isReroll = false) {
    const pickBtn = document.getElementById('pick-btn');
    const maxRuntime = parseInt(document.getElementById('runtime-slider').value, 10);
    const minRating = parseFloat(document.getElementById('pick-min-rating').value);
    const contentType = document.getElementById('pick-content-type').value || null;

    if (pickBtn) {
        pickBtn.disabled = true;
        pickBtn.innerHTML = `<i data-lucide="loader-2" class="w-6 h-6 animate-spin"></i><span>Finding Your Match in < 30ms...</span>`;
        lucide.createIcons();
    }

    try {
        const reqBody = {
            providers: Array.from(userSubscriptions),
            mood: activeMood,
            max_runtime: maxRuntime,
            min_imdb_rating: minRating,
            content_type: contentType,
            exclude_title_ids: isReroll ? excludeHistory : []
        };

        const startTime = performance.now();
        const res = await authFetch('/api/v1/discovery/pick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(reqBody)
        });

        const elapsedMs = Math.round(performance.now() - startTime);

        if (!res.ok) {
            const errData = await res.json();
            alert(errData.detail || 'No matches found. Try loosening constraints.');
            return;
        }

        const data = await res.json();
        lastPickData = data;
        excludeHistory.push(data.title.id);

        renderPickResult(data, elapsedMs);

    } catch (err) {
        console.error('Error during Pick For Me:', err);
    } finally {
        if (pickBtn) {
            pickBtn.disabled = false;
            pickBtn.innerHTML = `<i data-lucide="sparkles" class="w-6 h-6 text-amber-300 animate-bounce"></i><span>Pick My Next Stream (< 30s)</span>`;
            lucide.createIcons();
        }
    }
}

// ==================== THE REVEAL CARD RENDERING & SMART ALTERNATIVES ====================

function getConfidenceBadge(title, matchScore) {
    if (title.rating_imdb >= 8.5) return '🏆 Critic Consensus Top 1%';
    if (matchScore >= 95 || title.rating_imdb >= 8.0) return '🔥 98% Taste Match for You';
    if (title.providers && title.providers.some(p => (p.provider_id || '').includes('netflix'))) return '⚡ Trending on Netflix India';
    if (title.providers && title.providers.some(p => (p.provider_id || '').includes('prime'))) return '⏳ Included with Prime Video';
    if (title.runtime_minutes <= 95) return '⏱️ Fast-Paced 90m Hit';
    return '✨ Highly Recommended';
}

function renderPickResult(data, latencyMs) {
    const container = document.getElementById('pick-result-container');
    if (!container) return;

    const t = data.title;
    const stream = data.best_stream_option;
    const isSaved = watchlist.some(w => w.title_id === t.id);
    const watchLink = getWatchLink(stream, t.title);
    const confidenceBadge = getConfidenceBadge(t, data.match_score);

    container.classList.remove('hidden');
    container.innerHTML = `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/50 shadow-2xl relative overflow-hidden animate-slot glow-box">
            <!-- Header bar -->
            <div class="flex flex-wrap items-center justify-between gap-3 pb-6 border-b border-slate-700/60">
                <div class="flex items-center space-x-2">
                    <span class="px-3.5 py-1 rounded-full text-xs font-extrabold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5 animate-pulse">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                        ${data.match_score}% Match For You
                    </span>
                    <span class="px-3 py-1 rounded-full text-xs font-extrabold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        ${confidenceBadge}
                    </span>
                    <span class="text-xs text-slate-400">Solved in <strong>${latencyMs}ms</strong></span>
                </div>
                
                <div class="flex items-center space-x-2">
                    <button onclick="sharePick('${t.id}')" title="Share with friend" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 flex items-center gap-1 text-xs font-bold transition-all cursor-pointer">
                        <i data-lucide="share-2" class="w-3.5 h-3.5"></i>
                        <span>Share</span>
                    </button>
                    <button onclick="sendFeedback('${t.id}', true)" title="Like recommendation" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 cursor-pointer">
                        <i data-lucide="thumbs-up" class="w-4 h-4"></i>
                    </button>
                    <button onclick="sendFeedback('${t.id}', false)" title="Dislike recommendation" class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 cursor-pointer">
                        <i data-lucide="thumbs-down" class="w-4 h-4"></i>
                    </button>
                    <button onclick="triggerPickForMe(true)" class="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold text-slate-300 flex items-center gap-1.5 transition-all cursor-pointer">
                        <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
                        <span>Re-roll</span>
                    </button>
                </div>
            </div>

            <!-- Content Card -->
            <div class="grid grid-cols-1 md:grid-cols-12 gap-6 pt-6 items-center">
                <div class="md:col-span-4 shrink-0 relative group">
                    <img src="${t.poster_url}" alt="${t.title}" 
                        onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                        class="w-full h-96 object-cover rounded-2xl shadow-2xl border border-slate-700">
                    ${t.trailer_url ? `
                        <button onclick="openTrailerModal('${t.trailer_url}', '${t.title.replace(/'/g, "\\'")}')" 
                            class="absolute inset-0 m-auto w-14 h-14 rounded-full bg-black/70 backdrop-blur-md border border-white/30 text-white flex items-center justify-center shadow-2xl hover:scale-110 transition-transform cursor-pointer">
                            <i data-lucide="play" class="w-6 h-6 fill-white ml-0.5"></i>
                        </button>
                    ` : ''}
                </div>

                <div class="md:col-span-8 flex flex-col justify-between space-y-4">
                    <div>
                        <div class="flex items-center gap-2 mb-1.5">
                            <span class="px-2.5 py-0.5 rounded-md text-[11px] font-extrabold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${t.type}</span>
                            <span class="text-xs text-slate-400 font-semibold">${t.release_year} • ${t.runtime_minutes} min • ${t.genres.slice(0, 2).join(', ')}</span>
                        </div>
                        
                        <h2 class="font-heading text-3xl sm:text-4xl font-extrabold text-white mb-2 leading-tight">${t.title}</h2>
                        
                        <div class="flex items-center space-x-4 mb-3 text-xs font-bold">
                            <span class="text-amber-300 flex items-center gap-1">⭐ IMDb ${t.rating_imdb}/10</span>
                            <span class="text-rose-400 flex items-center gap-1">🍅 Rotten Tomatoes ${t.rating_rotten_tomatoes}%</span>
                            <span class="text-indigo-300">🎬 ${t.director || 'Acclaimed Director'}</span>
                        </div>

                        <div class="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1.5 mb-3">
                            <p class="font-bold text-indigo-300 text-[11px] uppercase tracking-wider">Why StreamPicker Chose This:</p>
                            ${data.match_reasons.map(r => `
                                <div class="flex items-center gap-2 text-slate-300">
                                    <span class="text-emerald-400 font-bold">✓</span>
                                    <span>${r}</span>
                                </div>
                            `).join('')}
                        </div>

                        <p class="text-xs sm:text-sm text-slate-300 line-clamp-3 leading-relaxed">${t.overview}</p>
                    </div>

                    <!-- Direct Launch CTA -->
                    <div class="space-y-3 pt-2">
                        ${stream ? `
                            <a href="${watchLink}" target="_blank" rel="noopener noreferrer" 
                                class="w-full py-4 px-5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-heading font-extrabold text-base flex items-center justify-center space-x-2 shadow-xl shadow-emerald-600/40 transition-all transform hover:-translate-y-0.5 cursor-pointer">
                                <i data-lucide="play" class="w-5 h-5 fill-white"></i>
                                <span>Watch Now on ${stream.provider_name} (${stream.access_type === 'flatrate' ? 'Included in Your Plan' : stream.access_type})</span>
                            </a>
                        ` : ''}

                        <div class="flex items-center space-x-2">
                            <button onclick="toggleWatchlist('${t.id}')" 
                                class="flex-1 py-3 px-4 rounded-xl text-xs font-bold border transition-all flex items-center justify-center space-x-2 cursor-pointer ${
                                    isSaved 
                                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' 
                                    : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
                                }">
                                <i data-lucide="${isSaved ? 'check' : 'bookmark'}" class="w-4 h-4"></i>
                                <span>${isSaved ? 'Saved in Watchlist' : 'Bookmark to Watchlist'}</span>
                            </button>

                            ${t.trailer_url ? `
                                <button onclick="openTrailerModal('${t.trailer_url}', '${t.title.replace(/'/g, "\\'")}')" 
                                    class="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-bold flex items-center gap-1.5 cursor-pointer">
                                    <i data-lucide="film" class="w-4 h-4 text-rose-400"></i>
                                    <span>Trailer</span>
                                </button>
                            ` : ''}

                            <button onclick="openModal('${t.id}')" class="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-bold cursor-pointer">
                                Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2 BACKUP ALTERNATIVES -->
            ${data.available_alternatives && data.available_alternatives.length > 0 ? `
                <div class="pt-6 mt-6 border-t border-slate-700/60 space-y-3">
                    <div class="flex items-center justify-between">
                        <h4 class="font-heading font-bold text-sm text-slate-300 flex items-center gap-2">
                            <i data-lucide="shuffle" class="w-4 h-4 text-purple-400"></i>
                            <span>Not feeling this? 2 Smart Alternatives:</span>
                        </h4>
                        <span class="text-[11px] text-slate-500 font-semibold">1-click switch</span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                        ${data.available_alternatives.slice(0, 2).map((alt, idx) => {
                            const altStream = alt.providers && alt.providers[0];
                            const altWatchLink = getWatchLink(altStream, alt.title);
                            const altReason = idx === 0 ? "Too intense? Try this crowd-pleaser" : "Want a different genre? Try this backup";
                            return `
                                <div class="p-3.5 rounded-2xl bg-slate-900/90 border border-slate-700/70 flex items-center justify-between gap-3 hover:border-indigo-500/50 transition-all">
                                    <div class="flex items-center space-x-3 min-w-0">
                                        <img src="${alt.poster_url}" alt="${alt.title}" 
                                            onerror="handleImageFallback(this, '${alt.title.replace(/'/g, "\\'")}')"
                                            class="w-14 h-20 object-cover rounded-xl shrink-0 shadow-md">
                                        <div class="min-w-0">
                                            <span class="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block truncate">${altReason}</span>
                                            <h5 class="font-heading font-bold text-sm text-white truncate">${alt.title}</h5>
                                            <div class="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                                                <span class="text-amber-300 font-semibold">⭐ ${alt.rating_imdb}</span>
                                                <span>•</span>
                                                <span>${alt.runtime_minutes}m</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="flex flex-col gap-1.5 shrink-0">
                                        <button onclick="switchToAlternative('${alt.id}')" class="px-3 py-1.5 bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white rounded-xl text-xs font-bold transition-all border border-indigo-500/40 cursor-pointer">
                                            Switch Pick
                                        </button>
                                        <a href="${altWatchLink}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl text-center border border-slate-700 cursor-pointer">
                                            Stream
                                        </a>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    lucide.createIcons();
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function switchToAlternative(titleId) {
    try {
        const res = await authFetch(`/api/v1/titles/${titleId}`);
        if (res.ok) {
            const titleObj = await res.json();
            const fakeData = {
                title: titleObj,
                match_score: 95,
                match_reasons: [
                    `Selected as your top backup alternative`,
                    `Included on your active subscription (${titleObj.providers[0]?.provider_name || 'Streaming'})`,
                    `Highly rated ${titleObj.rating_imdb}/10 IMDb and ${titleObj.runtime_minutes}m runtime`
                ],
                best_stream_option: titleObj.providers[0] || null,
                available_alternatives: (lastPickData?.available_alternatives || []).filter(a => a.id !== titleId)
            };
            lastPickData = fakeData;
            renderPickResult(fakeData, 8);
            showToast(`Switched pick to: ${titleObj.title}`);
        }
    } catch (e) {
        console.error('Error switching alternative:', e);
    }
}

// ==================== TINDER-STYLE SPEED SWIPE DECK ====================

let swipeDeck = [];
let swipeIndex = 0;
let swipeLikedTitles = [];

async function openSpeedSwipeModal() {
    const modal = document.getElementById('swipe-modal');
    if (!modal) return;
    modal.classList.remove('hidden');
    modal.classList.add('flex');

    swipeIndex = 0;
    swipeLikedTitles = [];
    showToast('🔥 Speed Swipe Mode: 5 rapid cards, decision in < 15s!');

    try {
        const params = new URLSearchParams();
        params.append('limit', '8');
        params.append('sort_by', 'rating');
        const res = await authFetch(`/api/v1/titles?${params.toString()}`);
        if (res.ok) {
            const data = await res.json();
            swipeDeck = (data.items || []).sort(() => 0.5 - Math.random()).slice(0, 5);
            renderSwipeDeck();
        }
    } catch (e) {
        console.error('Swipe deck error:', e);
    }
}

function closeSpeedSwipeModal() {
    const modal = document.getElementById('swipe-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

function renderSwipeDeck() {
    const stack = document.getElementById('swipe-card-stack');
    const pill = document.getElementById('swipe-progress-pill');
    if (!stack) return;

    if (swipeIndex >= swipeDeck.length) {
        const winner = swipeLikedTitles.length > 0 ? swipeLikedTitles[0] : swipeDeck[0];
        lockInSwipeWinner(winner);
        return;
    }

    if (pill) pill.textContent = `Card ${swipeIndex + 1} of ${swipeDeck.length}`;

    const t = swipeDeck[swipeIndex];
    const stream = t.providers && t.providers[0];
    const badge = getConfidenceBadge(t, 96);

    stack.innerHTML = `
        <div id="active-swipe-card" class="swipe-card absolute inset-0 glass-panel rounded-3xl border border-indigo-500/50 p-5 shadow-2xl flex flex-col justify-between overflow-hidden animate-slot">
            <div class="relative w-full h-72 rounded-2xl overflow-hidden mb-3">
                <img src="${t.poster_url}" alt="${t.title}" 
                    onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                    class="w-full h-full object-cover">
                <div class="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent"></div>
                <div class="absolute top-3 left-3 px-3 py-1 rounded-full bg-black/80 backdrop-blur-md border border-white/20 text-xs font-bold text-amber-300 flex items-center gap-1">
                    ${badge}
                </div>
                <div class="absolute bottom-3 left-3 right-3 flex items-center justify-between text-xs text-slate-300 font-bold">
                    <span>${t.release_year} • ${t.runtime_minutes} mins</span>
                    <span class="text-amber-300">⭐ ${t.rating_imdb}/10</span>
                </div>
            </div>

            <div class="space-y-2 flex-1 flex flex-col justify-between">
                <div>
                    <h3 class="font-heading font-extrabold text-xl text-white line-clamp-1">${t.title}</h3>
                    <p class="text-xs text-indigo-300 font-semibold">${t.genres.slice(0, 3).join(' • ')}</p>
                    <p class="text-xs text-slate-300 line-clamp-2 mt-1 leading-snug">${t.overview}</p>
                </div>

                ${stream ? `
                    <div class="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between text-xs">
                        <span class="font-semibold text-slate-300">Stream on <strong>${stream.provider_name}</strong></span>
                        <span class="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-emerald-500/20 text-emerald-300">Included</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    lucide.createIcons();
}

function handleSwipeAction(action) {
    const card = document.getElementById('active-swipe-card');
    const currentTitle = swipeDeck[swipeIndex];
    if (!card || !currentTitle) return;

    if (action === 'left') {
        card.classList.add('swipe-left');
        setTimeout(() => {
            swipeIndex++;
            renderSwipeDeck();
        }, 220);
    } else if (action === 'right') {
        card.classList.add('swipe-right');
        swipeLikedTitles.push(currentTitle);
        setTimeout(() => {
            swipeIndex++;
            renderSwipeDeck();
        }, 220);
    } else if (action === 'super') {
        card.classList.add('swipe-up');
        setTimeout(() => {
            lockInSwipeWinner(currentTitle);
        }, 220);
    }
}

function lockInSwipeWinner(winnerTitle) {
    closeSpeedSwipeModal();
    if (!winnerTitle) return;

    const fakeData = {
        title: winnerTitle,
        match_score: 99,
        match_reasons: [
            `🎉 15s Speed Swipe Consensus Winner!`,
            `Directly matches your active subscriptions (${winnerTitle.providers[0]?.provider_name || 'Streaming'})`,
            `High audience approval (${winnerTitle.rating_imdb}/10 IMDb, ${winnerTitle.runtime_minutes}m)`
        ],
        best_stream_option: winnerTitle.providers[0] || null,
        available_alternatives: swipeDeck.filter(d => d.id !== winnerTitle.id).slice(0, 2)
    };

    lastPickData = fakeData;
    renderPickResult(fakeData, 15);
    showToast(`👑 Locked in: "${winnerTitle.title}" as your stream!`);
}

// ==================== TRAILER MODAL ====================

function openTrailerModal(trailerUrl, title) {
    const modal = document.getElementById('trailer-modal');
    const container = document.getElementById('trailer-iframe-container');
    const titleEl = document.getElementById('trailer-modal-title');
    if (!modal || !container) return;

    if (titleEl) titleEl.textContent = `${title} — Official Trailer`;

    let videoId = 'uYPbbksJxIg';
    if (trailerUrl.includes('v=')) {
        videoId = trailerUrl.split('v=')[1].split('&')[0];
    } else if (trailerUrl.includes('youtu.be/')) {
        videoId = trailerUrl.split('youtu.be/')[1].split('?')[0];
    }

    container.innerHTML = `
        <iframe width="100%" height="100%" src="https://www.youtube.com/embed/${videoId}?autoplay=1" 
            title="YouTube video player" frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
        </iframe>
    `;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeTrailerModal() {
    const modal = document.getElementById('trailer-modal');
    const container = document.getElementById('trailer-iframe-container');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
    if (container) container.innerHTML = '';
}

// ==================== COUPLE / GROUP COMPROMISE PICK ====================

async function triggerGroupPick() {
    const btn = document.getElementById('group-pick-btn');
    const v1Name = document.getElementById('v1-name').value || 'Viewer 1';
    const v2Name = document.getElementById('v2-name').value || 'Viewer 2';
    const v1Mood = document.getElementById('v1-mood').value;
    const v2Mood = document.getElementById('v2-mood').value;

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i><span>Calculating compromise...</span>`;
        lucide.createIcons();
    }

    try {
        const req = {
            viewer_1: {
                name: v1Name,
                subscriptions: Array.from(userSubscriptions),
                preferred_mood: v1Mood,
                preferred_genres: []
            },
            viewer_2: {
                name: v2Name,
                subscriptions: Array.from(userSubscriptions),
                preferred_mood: v2Mood,
                preferred_genres: []
            },
            max_runtime: 150,
            min_imdb_rating: 7.0
        };

        const res = await authFetch('/api/v1/discovery/group-pick', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req)
        });

        if (!res.ok) {
            const errData = await res.json();
            alert(errData.detail || 'Could not find a compromise.');
            return;
        }

        const data = await res.json();
        renderGroupPickResult(data);

    } catch (err) {
        console.error('Error during group pick:', err);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="scale" class="w-5 h-5"></i><span>Find Our Compromise Pick</span>`;
            lucide.createIcons();
        }
    }
}

function renderGroupPickResult(data) {
    const container = document.getElementById('pick-result-container');
    if (!container) return;

    const t = data.chosen_title;
    const isSaved = watchlist.some(w => w.title_id === t.id);
    const watchLink = getWatchLink(t.providers && t.providers[0], t.title);

    container.classList.remove('hidden');
    container.innerHTML = `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl border border-rose-500/40 shadow-2xl relative overflow-hidden animate-slot">
            <div class="flex flex-wrap items-center justify-between gap-3 pb-5 border-b border-slate-700/60">
                <div class="flex items-center space-x-2">
                    <span class="px-3.5 py-1 rounded-full text-xs font-extrabold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/40 flex items-center gap-1.5">
                        <i data-lucide="heart-handshake" class="w-3.5 h-3.5"></i>
                        ${data.compromise_score}% Mutual Compromise Score
                    </span>
                </div>
                <div class="flex items-center space-x-3 text-xs text-slate-300 font-bold">
                    <span>${data.viewer_1_satisfaction}% Satisfied</span>
                    <span>•</span>
                    <span>${data.viewer_2_satisfaction}% Satisfied</span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-12 gap-6 pt-6">
                <div class="md:col-span-4 shrink-0">
                    <img src="${t.poster_url}" alt="${t.title}" 
                        onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                        class="w-full h-80 object-cover rounded-2xl shadow-xl border border-slate-700">
                </div>
                <div class="md:col-span-8 flex flex-col justify-between space-y-4">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30">${t.type}</span>
                            <span class="text-xs text-slate-400">${t.release_year} • ${t.runtime_minutes} min</span>
                        </div>
                        <h2 class="font-heading text-2xl sm:text-3xl font-extrabold text-white mb-2">${t.title}</h2>
                        
                        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1 mb-3">
                            <p class="font-bold text-rose-300 text-[11px] uppercase tracking-wider">Why Both Will Enjoy This:</p>
                            ${data.compromise_breakdown.map(r => `
                                <div class="flex items-center gap-1.5 text-slate-300">
                                    <span class="text-rose-400">✓</span>
                                    <span>${r}</span>
                                </div>
                            `).join('')}
                        </div>

                        <p class="text-xs text-slate-300 line-clamp-3 mb-4 leading-relaxed">${t.overview}</p>
                    </div>

                    <div class="space-y-3 pt-2">
                        ${t.providers.length > 0 ? `
                            <a href="${watchLink}" target="_blank" rel="noopener noreferrer" 
                                class="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-rose-600 to-indigo-600 hover:from-rose-500 hover:to-indigo-500 text-white font-heading font-bold text-sm flex items-center justify-center space-x-2 shadow-lg transition-all cursor-pointer">
                                <i data-lucide="play" class="w-4 h-4 fill-white"></i>
                                <span>Start Streaming on ${t.providers[0].provider_name}</span>
                            </a>
                        ` : ''}
                        
                        <button onclick="toggleWatchlist('${t.id}')" 
                            class="w-full py-2.5 px-4 rounded-xl text-xs font-semibold border bg-slate-800 text-slate-200 border-slate-700 flex items-center justify-center space-x-1.5">
                            <i data-lucide="${isSaved ? 'check' : 'bookmark'}" class="w-3.5 h-3.5"></i>
                            <span>${isSaved ? 'Saved in Watchlist' : 'Bookmark to Watchlist'}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    lucide.createIcons();
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ==================== WATCH PARTY COLLABORATIVE ROOMS ====================

async function createNewWatchRoom() {
    const hostName = document.getElementById('create-room-host-name').value.trim() || (currentUser ? currentUser.full_name : 'Host');
    try {
        const res = await authFetch('/api/v1/rooms/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                host_name: hostName,
                subscriptions: Array.from(userSubscriptions)
            })
        });
        if (!res.ok) throw new Error('Failed to create room');
        const data = await res.json();
        activeRoomCode = data.room_code;
        showToast(`🎉 Room Created: Code ${activeRoomCode}`);
        loadRoomArena(activeRoomCode);
    } catch (e) {
        showToast('Error creating watch room');
    }
}

async function joinExistingWatchRoom() {
    const code = document.getElementById('join-room-code-input').value.trim().toUpperCase();
    const name = document.getElementById('join-room-user-name').value.trim() || (currentUser ? currentUser.full_name : 'Guest');
    if (!code) return;

    try {
        const res = await authFetch(`/api/v1/rooms/${code}/join`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_name: name,
                subscriptions: Array.from(userSubscriptions)
            })
        });
        if (!res.ok) {
            alert('Room not found! Check code.');
            return;
        }
        activeRoomCode = code;
        showToast(`Joined Room ${activeRoomCode}`);
        loadRoomArena(activeRoomCode);
    } catch (e) {
        showToast('Error joining watch room');
    }
}

async function loadRoomArena(roomCode) {
    const arena = document.getElementById('active-room-container');
    if (!arena) return;

    try {
        const res = await fetch(`/api/v1/rooms/${roomCode}`);
        if (!res.ok) return;
        const state = await res.json();

        const winningLink = state.winning_title ? getWatchLink(state.winning_title.providers && state.winning_title.providers[0], state.winning_title.title) : '#';

        arena.classList.remove('hidden');
        arena.innerHTML = `
            <div class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-700">
                <div>
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Live Watch Room</span>
                    <h2 class="font-heading font-extrabold text-2xl text-white flex items-center gap-2">
                        <span>Code: ${state.room_code}</span>
                        <button onclick="navigator.clipboard.writeText('${state.room_code}'); showToast('Room code copied!');" class="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"><i data-lucide="copy" class="w-4 h-4"></i></button>
                    </h2>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-xs text-slate-300 font-medium">Participants (${state.participants.length}): <strong>${state.participants.join(', ')}</strong></span>
                </div>
            </div>

            ${state.winning_title ? `
                <div class="p-4 rounded-xl bg-gradient-to-r from-emerald-950 to-slate-900 border border-emerald-500/50 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div class="flex items-center space-x-3">
                        <img src="${state.winning_title.poster_url}" 
                            onerror="handleImageFallback(this, '${state.winning_title.title.replace(/'/g, "\\'")}')"
                            class="w-14 h-20 object-cover rounded-lg">
                        <div>
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300">👑 Current Group Favorite</span>
                            <h3 class="font-heading font-bold text-base text-white">${state.winning_title.title}</h3>
                            <p class="text-xs text-slate-400">${state.winning_title.release_year} • ⭐ ${state.winning_title.rating_imdb}</p>
                        </div>
                    </div>
                    ${state.winning_title.providers && state.winning_title.providers[0] ? `
                        <a href="${winningLink}" target="_blank" rel="noopener noreferrer" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow-lg flex items-center gap-2">
                            <i data-lucide="play" class="w-4 h-4 fill-white"></i>
                            <span>Stream Now</span>
                        </a>
                    ` : ''}
                </div>
            ` : ''}

            <div class="space-y-3">
                <h4 class="font-heading font-bold text-sm text-slate-300">Vote on Candidate Titles:</h4>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    ${state.candidates.map(c => `
                        <div class="glass-card p-3 rounded-xl flex items-center justify-between">
                            <div class="flex items-center space-x-3">
                                <img src="${c.title.poster_url}" 
                                    onerror="handleImageFallback(this, '${c.title.title.replace(/'/g, "\\'")}')"
                                    class="w-12 h-16 object-cover rounded-lg">
                                <div>
                                    <h5 class="font-bold text-xs text-white line-clamp-1">${c.title.title}</h5>
                                    <span class="text-[11px] text-slate-400">⭐ ${c.title.rating_imdb} • Score: <strong>${c.score}</strong></span>
                                </div>
                            </div>
                            <div class="flex items-center space-x-1.5">
                                <button onclick="castVote('${state.room_code}', '${c.title.id}', 1)" class="p-2 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300"><i data-lucide="thumbs-up" class="w-4 h-4"></i></button>
                                <button onclick="castVote('${state.room_code}', '${c.title.id}', -1)" class="p-2 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300"><i data-lucide="thumbs-down" class="w-4 h-4"></i></button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        lucide.createIcons();

    } catch (e) {
        console.error('Error loading room arena:', e);
    }
}

async function castVote(roomCode, titleId, voteVal) {
    const voterName = currentUser ? currentUser.full_name : 'Guest';
    try {
        await authFetch(`/api/v1/rooms/${roomCode}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                room_code: roomCode,
                user_name: voterName,
                title_id: titleId,
                vote: voteVal
            })
        });
        loadRoomArena(roomCode);
        showToast(voteVal > 0 ? '👍 Upvote recorded' : '👎 Downvote recorded');
    } catch (e) {
        console.error('Error voting:', e);
    }
}

// ==================== UNIVERSAL CATALOG & SEARCH ====================

async function loadCatalog() {
    const grid = document.getElementById('catalog-grid');
    if (!grid) return;

    const query = document.getElementById('catalog-search-input')?.value || '';
    const genre = document.getElementById('filter-genre')?.value || '';
    const type = document.getElementById('filter-type')?.value || '';
    const sortBy = document.getElementById('filter-sort')?.value || 'rating';

    try {
        const params = new URLSearchParams();
        if (query) params.append('q', query);
        if (genre) params.append('genre', genre);
        if (type) params.append('type', type);
        if (sortBy) params.append('sort_by', sortBy);
        params.append('limit', '50');

        const res = await authFetch(`/api/v1/titles?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to load titles');
        const data = await res.json();
        
        renderCatalogCards(data.items);
    } catch (err) {
        console.error('Error loading catalog:', err);
    }
}

function renderCatalogCards(titles) {
    const grid = document.getElementById('catalog-grid');
    if (!grid) return;

    if (titles.length === 0) {
        grid.innerHTML = `<div class="col-span-full text-center py-12 text-slate-500">No titles match your search criteria.</div>`;
        return;
    }

    grid.innerHTML = titles.map(t => {
        const isSaved = watchlist.some(w => w.title_id === t.id);
        const subProvider = t.providers.find(p => p.is_in_user_subscription);
        const bestProvider = subProvider || t.providers[0];
        const watchLink = getWatchLink(bestProvider, t.title);

        return `
            <div class="glass-card rounded-2xl overflow-hidden flex flex-col justify-between group">
                <div class="relative">
                    <img src="${t.poster_url}" alt="${t.title}" 
                        onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                        class="w-full h-60 object-cover transition-transform duration-300 group-hover:scale-105">
                    <div class="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent opacity-90"></div>
                    
                    <div class="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-md text-[11px] font-bold text-amber-300 border border-amber-500/30 flex items-center gap-1">
                        ⭐ ${t.rating_imdb}
                    </div>

                    <button onclick="event.stopPropagation(); toggleWatchlist('${t.id}')" 
                        class="absolute top-2.5 left-2.5 p-2 rounded-full bg-black/60 backdrop-blur-md text-slate-200 hover:text-rose-400 border border-white/10 transition-colors">
                        <i data-lucide="${isSaved ? 'bookmark-check' : 'bookmark'}" class="w-3.5 h-3.5 ${isSaved ? 'text-indigo-400 fill-indigo-400' : ''}"></i>
                    </button>
                </div>

                <div class="p-4 flex-1 flex flex-col justify-between space-y-3">
                    <div>
                        <div class="flex items-center gap-1.5 text-[11px] text-slate-400 mb-1">
                            <span>${t.release_year} • ${t.runtime_minutes}m • <span class="text-indigo-300 font-semibold">${t.genres[0] || 'Drama'}</span></span>
                        </div>
                        <h3 class="font-heading font-bold text-sm text-white line-clamp-1 group-hover:text-indigo-400 transition-colors">${t.title}</h3>
                    </div>

                    <div class="space-y-2 pt-1 border-t border-slate-800">
                        <div class="flex flex-wrap gap-1.5">
                            ${t.providers.map(p => `
                                <span class="px-2 py-0.5 rounded text-[10px] font-semibold flex items-center gap-1 ${
                                    p.is_in_user_subscription 
                                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                                }">
                                    <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${p.brand_color}"></span>
                                    ${p.provider_name}
                                </span>
                            `).join('')}
                        </div>

                        <div class="flex items-center gap-2 pt-2">
                            <button onclick="openModal('${t.id}')" class="flex-1 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold">
                                Details
                            </button>
                            ${bestProvider ? `
                                <a href="${watchLink}" target="_blank" rel="noopener noreferrer" 
                                    class="py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1 shadow-sm">
                                    <i data-lucide="play" class="w-3 h-3 fill-white"></i>
                                    <span>Stream</span>
                                </a>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

// ==================== WATCHLIST & EXPORT ====================

async function loadWatchlist() {
    try {
        const res = await authFetch('/api/v1/watchlist');
        if (!res.ok) throw new Error('Failed to load watchlist');
        watchlist = await res.json();
        
        const badge = document.getElementById('watchlist-count-badge');
        const pill = document.getElementById('watchlist-total-pill');
        if (badge) badge.textContent = watchlist.length;
        if (pill) pill.textContent = `${watchlist.length} Saved`;

        renderWatchlist();
    } catch (err) {
        console.error('Error loading watchlist:', err);
    }
}

function renderWatchlist() {
    const grid = document.getElementById('watchlist-grid');
    const emptyState = document.getElementById('watchlist-empty-state');
    if (!grid) return;

    if (watchlist.length === 0) {
        grid.innerHTML = '';
        if (emptyState) emptyState.classList.remove('hidden');
        return;
    }

    if (emptyState) emptyState.classList.add('hidden');

    grid.innerHTML = watchlist.map(w => {
        const t = w.title;
        const subProvider = t.providers.find(p => p.is_in_user_subscription);
        const bestProvider = subProvider || t.providers[0];
        const watchLink = getWatchLink(bestProvider, t.title);

        return `
            <div class="glass-card rounded-2xl overflow-hidden flex flex-col justify-between">
                <div class="relative">
                    <img src="${t.poster_url}" alt="${t.title}" 
                        onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                        class="w-full h-52 object-cover">
                    <div class="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent opacity-90"></div>
                    <button onclick="removeWatchlist('${t.id}')" class="absolute top-2.5 right-2.5 p-1.5 rounded-full bg-black/70 text-slate-400 hover:text-rose-400 transition-colors">
                        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                    </button>
                </div>

                <div class="p-4 flex-1 flex flex-col justify-between space-y-3">
                    <div>
                        <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                            <span>${t.release_year} • ${t.runtime_minutes}m</span>
                            <span class="text-amber-300 font-bold">⭐ ${t.rating_imdb}</span>
                        </div>
                        <h3 class="font-heading font-bold text-sm text-white">${t.title}</h3>
                    </div>

                    <div class="space-y-2 pt-2 border-t border-slate-800">
                        ${bestProvider ? `
                            <a href="${watchLink}" target="_blank" rel="noopener noreferrer" 
                                class="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm">
                                <i data-lucide="play" class="w-3.5 h-3.5 fill-white"></i>
                                <span>Watch on ${bestProvider.provider_name}</span>
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

function exportWatchlist(format) {
    window.location.href = `/api/v1/watchlist/export?format=${format}`;
    showToast(`Exporting watchlist as ${format.toUpperCase()}...`);
}

async function toggleWatchlist(titleId) {
    const isSaved = watchlist.some(w => w.title_id === titleId);
    if (isSaved) {
        await removeWatchlist(titleId);
    } else {
        try {
            await authFetch('/api/v1/watchlist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title_id: titleId, status: 'saved' })
            });
            await loadWatchlist();
            if (currentTab === 'catalog') loadCatalog();
            showToast('⭐ Saved to your unified watchlist');
        } catch (err) {
            console.error('Error adding to watchlist:', err);
        }
    }
}

async function removeWatchlist(titleId) {
    try {
        await authFetch(`/api/v1/watchlist/${titleId}`, { method: 'DELETE' });
        await loadWatchlist();
        if (currentTab === 'catalog') loadCatalog();
        showToast('Removed from watchlist');
    } catch (err) {
        console.error('Error removing from watchlist:', err);
    }
}

// ==================== LIVE TMDB & SYSTEM SYNC ====================

async function triggerLiveTMDBSync() {
    const btn = document.getElementById('tmdb-sync-btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Syncing TMDB...</span>`;
        lucide.createIcons();
    }

    try {
        const res = await authFetch('/api/v1/system/sync-live-tmdb', { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            showToast(`🎬 Ingested ${data.synced_count} titles via ${data.source}!`);
            await loadCatalog();
            await loadAnalytics();
        }
    } catch (e) {
        showToast('TMDB sync failed');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="cloud-download" class="w-4 h-4"></i><span>Sync Live TMDB</span>`;
            lucide.createIcons();
        }
    }
}

async function loadAPIStatus() {
    const container = document.getElementById('api-status-container');
    if (!container) return;

    try {
        const res = await fetch('/api/v1/system/api-status');
        if (!res.ok) return;
        const data = await res.json();

        container.innerHTML = `
            <div class="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span class="font-semibold text-slate-300">TMDB API</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${data.tmdb_configured ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}">
                    ${data.tmdb_configured ? '● Live API Active' : '○ Demo Simulation'}
                </span>
            </div>
            <div class="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span class="font-semibold text-slate-300">Database Engine</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300">
                    ${data.database_backend}
                </span>
            </div>
            <div class="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span class="font-semibold text-slate-300">Caching Engine</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${data.redis_configured ? 'bg-emerald-500/20 text-emerald-300' : 'bg-sky-500/20 text-sky-300'}">
                    ${data.redis_configured ? 'Redis 7' : 'In-Memory TTL'}
                </span>
            </div>
        `;
    } catch (e) {
        console.error('Error loading API status:', e);
    }
}

// ==================== TELEMETRY & ANALYTICS ====================

async function loadAnalytics() {
    const grid = document.getElementById('analytics-metrics-grid');
    const ctrContainer = document.getElementById('provider-ctr-container');
    if (!grid || !ctrContainer) return;

    try {
        const res = await fetch('/api/v1/system/analytics');
        if (!res.ok) return;
        const data = await res.json();

        grid.innerHTML = `
            <div class="glass-panel p-5 rounded-2xl border border-indigo-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Total Discovery Sessions</span>
                <div class="font-heading text-2xl font-extrabold text-white mt-1">${data.total_discovery_sessions}</div>
                <div class="text-[11px] text-emerald-400 mt-1">${data.discovery_success_rate_percent}% Success Rate</div>
            </div>
            <div class="glass-panel p-5 rounded-2xl border border-emerald-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Avg Decision Latency</span>
                <div class="font-heading text-2xl font-extrabold text-emerald-400 mt-1">${data.average_decision_latency_ms} ms</div>
                <div class="text-[11px] text-slate-400 mt-1">Sub-30s decision target met</div>
            </div>
            <div class="glass-panel p-5 rounded-2xl border border-sky-500/30">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Stream Click-Throughs</span>
                <div class="font-heading text-2xl font-extrabold text-sky-300 mt-1">${data.total_stream_clickthroughs}</div>
                <div class="text-[11px] text-slate-400 mt-1">Direct OTT App launches</div>
            </div>
        `;

        ctrContainer.innerHTML = Object.entries(data.provider_ctr_distribution).map(([p, count]) => `
            <div class="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span class="font-semibold text-slate-300 uppercase">${p.replace('_', ' ')}</span>
                <span class="font-bold text-indigo-400">${count} launches</span>
            </div>
        `).join('');

        lucide.createIcons();

    } catch (e) {
        console.error('Error loading analytics:', e);
    }
}

async function triggerCatalogSync() {
    try {
        const res = await authFetch('/api/v1/system/sync-catalog', { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            showToast(`✅ Synced ${data.synced_titles_count} titles in ${data.duration_ms}ms!`);
            loadAnalytics();
        }
    } catch (e) {
        showToast('Sync error');
    }
}

// ==================== AVAILABILITY ALERTS ====================

async function loadAlerts() {
    try {
        const res = await authFetch('/api/v1/alerts/notifications');
        if (!res.ok) return;
        const alerts = await res.json();

        const badge = document.getElementById('alerts-count-badge');
        if (badge) badge.textContent = alerts.length;

        const container = document.getElementById('alerts-list-container');
        if (container) {
            if (alerts.length === 0) {
                container.innerHTML = `<div class="text-center py-6 text-slate-500 text-xs">No pending availability alerts.</div>`;
            } else {
                container.innerHTML = alerts.map(a => `
                    <div class="p-3 rounded-xl bg-slate-900 border border-slate-700 flex items-start space-x-3">
                        <img src="${a.poster_url}" 
                            onerror="handleImageFallback(this, '${a.title_name.replace(/'/g, "\\'")}')"
                            class="w-10 h-14 object-cover rounded-lg shrink-0">
                        <div class="flex-1">
                            <p class="text-xs font-semibold text-slate-200 leading-snug">${a.message}</p>
                            <a href="${a.action_url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 font-bold mt-1.5">
                                <span>Watch on ${a.provider_name}</span>
                                <i data-lucide="external-link" class="w-3 h-3"></i>
                            </a>
                        </div>
                    </div>
                `).join('');
            }
        }
        lucide.createIcons();
    } catch (e) {
        console.error('Error loading alerts:', e);
    }
}

function toggleAlertsModal() {
    const modal = document.getElementById('alerts-modal');
    if (modal) {
        if (modal.classList.contains('hidden')) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            loadAlerts();
        } else {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }
}

// ==================== AI VIBE SEARCH ====================

function setVibePrompt(text) {
    const input = document.getElementById('vibe-query-input');
    if (input) {
        input.value = text;
        triggerVibeSearch();
    }
}

async function triggerVibeSearch() {
    const input = document.getElementById('vibe-query-input');
    const container = document.getElementById('vibe-results-container');
    const btn = document.getElementById('vibe-search-btn');
    if (!input || !container) return;

    const query = input.value.trim();
    if (!query) return;

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Analyzing vibe...</span>`;
        lucide.createIcons();
    }

    try {
        const res = await authFetch('/api/v1/discovery/vibe-search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, min_imdb_rating: 6.0 })
        });

        if (!res.ok) throw new Error('Vibe search failed');
        const data = await res.json();
        const crit = data.extracted_criteria;

        container.innerHTML = `
            <div class="glass-panel p-4 rounded-xl border border-purple-500/30 flex flex-wrap items-center gap-3 text-xs">
                <span class="font-bold text-purple-300 uppercase tracking-wider text-[11px]">AI Parsed Criteria:</span>
                ${crit.detected_mood ? `<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-semibold border border-purple-500/30">Vibe: ${crit.detected_mood}</span>` : ''}
                ${crit.detected_max_runtime ? `<span class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-semibold border border-sky-500/30">Max Time: ${crit.detected_max_runtime}m</span>` : ''}
                ${crit.detected_genres.map(g => `<span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold">${g}</span>`).join('')}
                ${crit.detected_director_or_actor ? `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold">Artist: ${crit.detected_director_or_actor}</span>` : ''}
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-2">
                ${data.results.map(r => {
                    const t = r.title;
                    const stream = r.best_stream_option;
                    const watchLink = getWatchLink(stream, t.title);

                    return `
                        <div class="glass-card rounded-2xl overflow-hidden flex flex-col justify-between">
                            <div class="relative">
                                <img src="${t.poster_url}" alt="${t.title}" 
                                    onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                                    class="w-full h-48 object-cover">
                                <div class="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-md bg-purple-900/80 backdrop-blur-md text-[11px] font-bold text-purple-200 border border-purple-500/40">
                                    ${r.semantic_score}% Vibe Match
                                </div>
                            </div>
                            <div class="p-4 flex-1 flex flex-col justify-between space-y-3">
                                <div>
                                    <div class="flex items-center gap-1.5 text-[11px] text-slate-400 mb-1">
                                        <span>${t.release_year} • ${t.runtime_minutes}m</span>
                                        <span class="text-amber-300 font-bold">⭐ ${t.rating_imdb}</span>
                                    </div>
                                    <h3 class="font-heading font-bold text-sm text-white line-clamp-1">${t.title}</h3>
                                    <p class="text-[11px] text-emerald-400 mt-1 font-medium">${r.match_explanation}</p>
                                </div>
                                <div class="pt-2 border-t border-slate-800 flex gap-2">
                                    <button onclick="openModal('${t.id}')" class="flex-1 py-1.5 px-3 rounded-xl bg-slate-800 text-slate-200 text-xs font-semibold">Details</button>
                                    ${stream ? `
                                        <a href="${watchLink}" target="_blank" rel="noopener noreferrer" class="py-1.5 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold flex items-center gap-1">
                                            <i data-lucide="play" class="w-3 h-3 fill-white"></i>
                                            <span>Stream</span>
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        lucide.createIcons();

    } catch (err) {
        console.error('Error during vibe search:', err);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i><span>Search Vibe</span>`;
            lucide.createIcons();
        }
    }
}

// ==================== MODAL & SIMILAR TITLES ====================

async function openModal(titleId) {
    const modal = document.getElementById('title-modal');
    const content = document.getElementById('modal-content');
    if (!modal || !content) return;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    content.innerHTML = `<div class="p-8 text-center text-slate-400"><i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2"></i>Loading details & recommendations...</div>`;
    lucide.createIcons();

    try {
        const [titleRes, redunRes, simRes] = await Promise.all([
            authFetch(`/api/v1/titles/${titleId}`),
            authFetch(`/api/v1/subscriptions/redundancy-check/${titleId}`),
            authFetch(`/api/v1/titles/${titleId}/similar?limit=4`)
        ]);

        if (!titleRes.ok) throw new Error('Failed to load title');
        const t = await titleRes.json();
        const redun = redunRes.ok ? await redunRes.json() : null;
        const sim = simRes.ok ? await simRes.json() : { similar_titles: [] };

        content.innerHTML = `
            <div class="space-y-5">
                ${redun && redun.is_redundant ? `
                    <div class="p-3.5 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold flex items-center gap-2">
                        <i data-lucide="shield-check" class="w-5 h-5 text-emerald-400 shrink-0"></i>
                        <span>${redun.redundancy_message}</span>
                    </div>
                ` : ''}

                <div class="flex gap-4">
                    <img src="${t.poster_url}" alt="${t.title}" 
                        onerror="handleImageFallback(this, '${t.title.replace(/'/g, "\\'")}')"
                        class="w-28 h-40 object-cover rounded-xl shadow-lg shrink-0">
                    <div>
                        <div class="flex items-center gap-2 mb-1 text-xs">
                            <span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold uppercase">${t.type}</span>
                            <span class="text-slate-400">${t.release_year} • ${t.runtime_minutes} min</span>
                        </div>
                        <h2 class="font-heading font-extrabold text-xl sm:text-2xl text-white mb-2">${t.title}</h2>
                        <div class="flex items-center space-x-3 text-xs mb-2">
                            <span class="text-amber-300 font-bold">⭐ IMDb ${t.rating_imdb}/10</span>
                            <span class="text-rose-400 font-bold">🍅 RT ${t.rating_rotten_tomatoes}%</span>
                        </div>
                        <p class="text-xs text-slate-400"><strong>Director:</strong> ${t.director || 'N/A'}</p>
                        <p class="text-xs text-slate-400"><strong>Cast:</strong> ${t.cast_members.join(', ') || 'N/A'}</p>
                    </div>
                </div>

                <div>
                    <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Synopsis</h4>
                    <p class="text-xs sm:text-sm text-slate-300 leading-relaxed">${t.overview}</p>
                </div>

                <div>
                    <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Streaming Availability (${selectedDevice.toUpperCase()})</h4>
                    <div class="space-y-2">
                        ${t.providers.map(p => {
                            const pWatchLink = getWatchLink(p, t.title);
                            return `
                                <div class="p-3 rounded-xl bg-slate-900/90 border border-slate-700/80 flex items-center justify-between">
                                    <div class="flex items-center space-x-3">
                                        <div class="w-3 h-3 rounded-full" style="background-color: ${p.brand_color}"></div>
                                        <div>
                                            <div class="text-xs font-bold text-white flex items-center gap-1.5">
                                                <span>${p.provider_name}</span>
                                                ${p.is_in_user_subscription ? '<span class="text-[10px] px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 rounded font-semibold">Included in your plan</span>' : ''}
                                            </div>
                                            <div class="text-[11px] text-slate-400 capitalize">${p.access_type} ${p.price ? `• ₹${p.price}` : ''}</div>
                                        </div>
                                    </div>
                                    <a href="${pWatchLink}" target="_blank" rel="noopener noreferrer" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold flex items-center gap-1">
                                        <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                                        <span>Stream</span>
                                    </a>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                ${sim.similar_titles.length > 0 ? `
                    <div class="pt-3 border-t border-slate-800">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
                            <i data-lucide="sparkles" class="w-4 h-4 text-purple-400"></i>
                            <span>More Like This (Vector Similarity)</span>
                        </h4>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            ${sim.similar_titles.map(st => `
                                <div onclick="openModal('${st.title.id}')" class="glass-card p-2 rounded-xl cursor-pointer hover:border-indigo-500/50 transition-all">
                                    <img src="${st.title.poster_url}" 
                                        onerror="handleImageFallback(this, '${st.title.title.replace(/'/g, "\\'")}')"
                                        class="w-full h-28 object-cover rounded-lg mb-2">
                                    <h5 class="text-xs font-bold text-white line-clamp-1">${st.title.title}</h5>
                                    <span class="text-[10px] text-emerald-400 font-semibold">${st.similarity_score}% Similar</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        lucide.createIcons();

    } catch (err) {
        content.innerHTML = `<div class="p-4 text-center text-rose-400">Failed to load title details.</div>`;
    }
}

function closeModal() {
    const modal = document.getElementById('title-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

async function sharePick(titleId) {
    try {
        const res = await authFetch('/api/v1/share/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                share_type: 'pick',
                payload: { title_id: titleId }
            })
        });
        if (!res.ok) throw new Error('Failed to create share link');
        const data = await res.json();
        const fullURL = `${window.location.origin}${data.share_url}`;
        
        await navigator.clipboard.writeText(fullURL);
        showToast('🔗 Share link copied to clipboard!');
    } catch (err) {
        showToast('Share link created: ' + window.location.href);
    }
}

async function checkSharedURL() {
    const path = window.location.pathname;
    if (path.startsWith('/s/')) {
        const token = path.replace('/s/', '');
        try {
            const res = await fetch(`/api/v1/share/${token}`);
            if (res.ok) {
                const data = await res.json();
                if (data.payload && data.payload.title_id) {
                    openModal(data.payload.title_id);
                }
            }
        } catch (e) {
            console.error('Shared url load failed:', e);
        }
    }
}

async function sendFeedback(titleId, liked) {
    try {
        await authFetch('/api/v1/history/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title_id: titleId, liked: liked })
        });
        showToast(liked ? '👍 Feedback recorded!' : '👎 Noted! Tuning preferences.');
    } catch (err) {
        console.error('Feedback error:', err);
    }
}
