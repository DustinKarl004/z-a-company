<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { getMonthly, getOverview } from "../api/dashboard";
import MonthYearPicker from "../components/MonthYearPicker.vue";
import LoadingState from "../components/LoadingState.vue";

const SERIES_COLORS = ["#ff2d4d", "#ff8a3d", "#ffe14d", "#4dd6ff", "#8a6bff", "#4dffb0", "#ff4dd2", "#c8c8c8"];

const overview = ref(null);
const monthly = ref(null);
const loading = ref(true);
const monthlyLoading = ref(false);

const now = new Date();
const selectedYear = ref(now.getFullYear());
const selectedMonth = ref(now.getMonth() + 1);

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

// --- Bar chart: profit by branch on a chosen date (defaults to today) ---
const profitDate = ref(todayIso());
const profitOverview = ref(null);
const profitLoading = ref(false);

function peso(amount) {
  return `₱${amount.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function niceMax(value) {
  if (value <= 0) return 10;
  const magnitude = Math.pow(10, Math.floor(Math.log10(value)));
  const scaled = value / magnitude;
  const step = scaled <= 1 ? 1 : scaled <= 2 ? 2 : scaled <= 5 ? 5 : 10;
  return step * magnitude;
}

async function loadOverview() {
  loading.value = true;
  overview.value = await getOverview();
  loading.value = false;
}

async function loadProfitOverview() {
  profitLoading.value = true;
  profitOverview.value = await getOverview(profitDate.value);
  profitLoading.value = false;
}

async function loadMonthly() {
  monthlyLoading.value = true;
  monthly.value = await getMonthly(selectedYear.value, selectedMonth.value);
  monthlyLoading.value = false;
}

onMounted(async () => {
  await Promise.all([loadOverview(), loadProfitOverview(), loadMonthly()]);
});

watch([selectedYear, selectedMonth], loadMonthly);
watch(profitDate, loadProfitOverview);

const alertCount = computed(() => overview.value?.branches.filter((b) => b.has_shortfall).length || 0);

// --- Bar chart: profit today by branch ---
const BAR_CHART_W = 600;
const BAR_CHART_H = 220;
const BAR_MARGIN = { top: 24, right: 16, bottom: 28, left: 16 };

const barChart = computed(() => {
  const branches = profitOverview.value?.branches || [];
  const innerW = BAR_CHART_W - BAR_MARGIN.left - BAR_MARGIN.right;
  const innerH = BAR_CHART_H - BAR_MARGIN.top - BAR_MARGIN.bottom;
  const maxVal = niceMax(Math.max(...branches.map((b) => b.profit), 0));
  const bandWidth = branches.length ? innerW / branches.length : innerW;
  const barWidth = Math.min(40, bandWidth * 0.5);

  const bars = branches.map((b, i) => {
    const bandCenter = BAR_MARGIN.left + bandWidth * (i + 0.5);
    const barHeight = maxVal > 0 ? (Math.max(b.profit, 0) / maxVal) * innerH : 0;
    return {
      id: b.branch_id,
      name: b.branch_name,
      value: b.profit,
      color: SERIES_COLORS[i % SERIES_COLORS.length],
      x: bandCenter - barWidth / 2,
      y: BAR_MARGIN.top + innerH - barHeight,
      width: barWidth,
      height: barHeight,
      labelX: bandCenter,
      nameY: BAR_MARGIN.top + innerH + 18,
    };
  });

  return { bars, innerH, baselineY: BAR_MARGIN.top + innerH };
});

const hoveredBar = ref(null);

// --- Donut chart: monthly sales share by branch ---
const DONUT_R = 70;
const DONUT_STROKE = 26;
const DONUT_CIRC = 2 * Math.PI * DONUT_R;

const donutChart = computed(() => {
  const branches = monthly.value?.branches || [];
  const total = monthly.value?.total_sales || 0;
  let cumulative = 0;
  const segments = branches.map((b, i) => {
    const pct = total > 0 ? b.total_sales / total : 0;
    const length = pct * DONUT_CIRC;
    const segment = {
      id: b.branch_id,
      name: b.branch_name,
      value: b.total_sales,
      pct,
      color: SERIES_COLORS[i % SERIES_COLORS.length],
      dasharray: `${length} ${DONUT_CIRC - length}`,
      dashoffset: -cumulative,
    };
    cumulative += length;
    return segment;
  });
  return { segments, total };
});
</script>

<template>
  <div class="dash">
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p class="page-subtitle">{{ overview ? new Date(overview.date).toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" }) : "" }}</p>
      </div>
    </div>

    <LoadingState v-if="loading" label="Loading dashboard..." />

    <template v-else-if="overview">
      <div class="stat-row">
        <div class="card stat-card">
          <span class="stat-label">Today's sales</span>
          <span class="stat-value">{{ peso(overview.total_sales) }}</span>
        </div>
        <div class="card stat-card">
          <span class="stat-label">This month's sales</span>
          <span class="stat-value">{{ monthly ? peso(monthly.total_sales) : "—" }}</span>
        </div>
        <div class="card stat-card">
          <span class="stat-label">Branches</span>
          <span class="stat-value">{{ overview.branch_count }}</span>
        </div>
        <div class="card stat-card" :class="{ 'stat-card-alert': alertCount > 0 }">
          <span class="stat-label">Stock alerts</span>
          <span class="stat-value">{{ alertCount }}</span>
        </div>
      </div>

      <div class="card chart-card" v-if="overview.branches.length">
        <div class="monthly-header">
          <h2 class="card-title">Daily profit by branch</h2>
          <input v-model="profitDate" type="date" :max="todayIso()" />
        </div>
        <LoadingState v-if="profitLoading" label="Loading profit..." />
        <div v-else class="chart-scroll">
          <svg
            class="bar-chart"
            :viewBox="`0 0 ${BAR_CHART_W} ${BAR_CHART_H}`"
            preserveAspectRatio="xMidYMid meet"
            role="img"
            :aria-label="`Bar chart of profit per branch on ${profitDate}`"
          >
            <defs>
              <linearGradient v-for="bar in barChart.bars" :key="bar.id" :id="`barGradient-${bar.id}`" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" :stop-color="bar.color" stop-opacity="1" />
                <stop offset="100%" :stop-color="bar.color" stop-opacity="0.35" />
              </linearGradient>
            </defs>
            <line
              class="baseline"
              :x1="0"
              :x2="BAR_CHART_W"
              :y1="barChart.baselineY"
              :y2="barChart.baselineY"
            />
            <g v-for="bar in barChart.bars" :key="bar.id">
              <rect
                class="bar"
                :class="{ 'bar-hover': hoveredBar === bar.id }"
                :x="bar.x"
                :y="bar.y"
                :width="bar.width"
                :height="Math.max(bar.height, 1)"
                rx="4"
                :fill="`url(#barGradient-${bar.id})`"
                :style="{ '--bar-glow': bar.color }"
                tabindex="0"
                @pointerenter="hoveredBar = bar.id"
                @pointerleave="hoveredBar = null"
                @focus="hoveredBar = bar.id"
                @blur="hoveredBar = null"
              />
              <text class="bar-value" :x="bar.labelX" :y="bar.y - 8" text-anchor="middle">
                {{ peso(bar.value) }}
              </text>
              <text class="bar-name" :x="bar.labelX" :y="bar.nameY" text-anchor="middle">
                {{ bar.name }}
              </text>
            </g>
          </svg>
        </div>
      </div>

      <div class="card chart-card">
        <div class="monthly-header">
          <h2 class="card-title">Monthly trend</h2>
          <MonthYearPicker v-model:year="selectedYear" v-model:month="selectedMonth" />
        </div>

        <LoadingState v-if="monthlyLoading" label="Loading monthly trend..." />
        <template v-else-if="monthly">
          <div v-if="donutChart.segments.length" class="donut-body">
            <svg
              class="donut-chart"
              viewBox="0 0 180 180"
              role="img"
              aria-label="Donut chart of this month's sales share per branch"
            >
              <circle
                class="donut-track"
                cx="90"
                cy="90"
                :r="DONUT_R"
                fill="none"
                :stroke-width="DONUT_STROKE"
              />
              <circle
                v-for="seg in donutChart.segments"
                :key="seg.id"
                class="donut-segment"
                cx="90"
                cy="90"
                :r="DONUT_R"
                fill="none"
                :stroke="seg.color"
                :stroke-width="DONUT_STROKE"
                :stroke-dasharray="seg.dasharray"
                :stroke-dashoffset="seg.dashoffset"
                transform="rotate(-90 90 90)"
              >
                <title>{{ seg.name }}: {{ peso(seg.value) }} ({{ (seg.pct * 100).toFixed(1) }}%)</title>
              </circle>
              <text class="donut-total" x="90" y="86" text-anchor="middle">Total</text>
              <text class="donut-total-value" x="90" y="104" text-anchor="middle">{{ peso(donutChart.total) }}</text>
            </svg>

            <ul class="branch-totals">
              <li v-for="seg in donutChart.segments" :key="seg.id">
                <span class="legend-swatch" :style="{ background: seg.color }"></span>
                <span class="branch-totals-name">{{ seg.name }}</span>
                <span class="branch-totals-value">{{ peso(seg.value) }}</span>
              </li>
              <li class="branch-totals-all">
                <span class="branch-totals-name">All branches</span>
                <span class="branch-totals-value">{{ peso(monthly.total_sales) }}</span>
              </li>
            </ul>
          </div>
          <p v-else class="empty-hint">No sales recorded this month yet.</p>
        </template>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dash {
  --dash-glow: rgba(255, 45, 77, 0.35);
}

.page-header {
  margin-bottom: 1.75rem;
  border-bottom: 1px solid var(--color-border);
}

.page-header h1 {
  font-size: 1.7rem;
  margin-bottom: 0.35rem;
  color: var(--color-text);
  letter-spacing: 0.02em;
}

.page-subtitle {
  color: var(--color-text-muted);
  margin: 0;
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}


.stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), transparent 70%);
}

.stat-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-value {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text);
  text-shadow: 0 0 18px var(--dash-glow);
}

.stat-card-alert .stat-value {
  color: var(--color-primary);
}

.chart-card {
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 0.95rem;
  margin-bottom: 1.25rem;
  color: var(--color-text);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.card-title::before {
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--dash-glow);
}

.empty-hint {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.monthly-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.monthly-header .card-title {
  margin-bottom: 0;
}

.chart-scroll {
  overflow-x: auto;
}

.bar-chart {
  width: 100%;
  min-width: 480px;
  height: 220px;
  overflow: visible;
}

.baseline {
  stroke: var(--color-border);
  stroke-width: 1;
}

.bar {
  transition: opacity 0.15s ease, filter 0.15s ease;
  cursor: pointer;
  filter: drop-shadow(0 0 6px var(--bar-glow, var(--dash-glow)));
}

.bar-hover {
  opacity: 0.85;
  filter: drop-shadow(0 0 14px var(--bar-glow, var(--dash-glow)));
}

.bar-value {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 12px;
  font-weight: 700;
  fill: var(--color-text);
}

.bar-name {
  font-size: 11px;
  fill: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.branch-totals {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  border-left: 1px solid var(--color-border);
  padding-left: 1.25rem;
}

.branch-totals li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.branch-totals-name {
  flex: 1;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.branch-totals-value {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-weight: 700;
  color: var(--color-text);
}

.branch-totals-all {
  margin-top: 0.4rem;
  padding-top: 0.6rem;
  border-top: 1px solid var(--color-border);
}

.branch-totals-all .branch-totals-name,
.branch-totals-all .branch-totals-value {
  color: var(--color-primary);
}

.donut-body {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1.5rem;
  align-items: center;
}

.donut-chart {
  width: 100%;
  max-width: 200px;
  height: auto;
}

.donut-track {
  stroke: var(--color-border);
}

.donut-segment {
  transition: opacity 0.15s ease;
}

.donut-total {
  font-size: 10px;
  fill: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.donut-total-value {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 13px;
  font-weight: 700;
  fill: var(--color-text);
}

.donut-body .branch-totals {
  border-left: none;
  padding-left: 0;
}

@media (max-width: 860px) {
  .stat-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .branch-totals {
    border-left: none;
    border-top: 1px solid var(--color-border);
    padding-left: 0;
    padding-top: 1rem;
  }

  .donut-body {
    grid-template-columns: 1fr;
    justify-items: center;
  }
}

@media (max-width: 500px) {
  .stat-row {
    grid-template-columns: 1fr;
  }

  .monthly-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
