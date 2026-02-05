<template>
  <div class="h-full w-full">
    <div
      v-if="item.type == 'number_chart'"
      class="flex h-full w-full rounded shadow overflow-hidden"
      :class="isClickable(item) ? 'cursor-pointer' : 'cursor-default'"
      @click="isClickable(item) && navigateToPage(item)"
    >
      <Tooltip :text="__(item.data.tooltip)">
        <NumberChart
          class="!items-start"
          v-if="item.data"
          :key="index"
          :config="item.data"
        />
      </Tooltip>
    </div>
    <div
      v-else-if="item.type == 'spacer'"
      class="rounded bg-surface-white h-full overflow-hidden text-ink-gray-5 flex items-center justify-center"
      :class="editing ? 'border border-dashed border-outline-gray-2' : ''"
    >
      {{ editing ? __('Spacer') : '' }}
    </div>
    <div
      v-else-if="item.type == 'axis_chart'"
      class="h-full w-full rounded-md bg-surface-white shadow"
    >
      <AxisChart v-if="item.data" :config="item.data" />
    </div>
    <div
      v-else-if="item.type == 'donut_chart'"
      class="h-full w-full rounded-md bg-surface-white shadow overflow-hidden"
    >
      <DonutChart v-if="item.data" :config="item.data" />
    </div>
  </div>
</template>
<script setup>
import { AxisChart, DonutChart, NumberChart, Tooltip } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { inject } from 'vue'

const router = useRouter()

const props = defineProps({
  index: {
    type: Number,
    required: true,
  },
  item: {
    type: Object,
    required: true,
  },
  editing: {
    type: Boolean,
    default: false,
  },
})

// Inject dashboard context filters if available
const fromDate = inject('fromDate', null)
const toDate = inject('toDate', null)
const dashboardFilters = inject('filters', null)

// Define which cards are clickable
function isClickable(item) {
  if (props.editing) return false; // Don't navigate when editing
  
  // Check if item and item name exist
  if (!item || !item.name) return false;
  
  // Normalize the item name for comparison
  const itemName = item.name.toLowerCase().trim();
  
  // Only allow specific cards to be clickable
  const clickableCards = [
    'total_leads',
    'ongoing_deals', 
    'won_deals',
    'lost_deals',
    'converted_leads'
  ];
  
  // Check if the item name matches any of our clickable cards
  return clickableCards.some(card => card === itemName);
}

function navigateToPage(item) {
  if (!isClickable(item)) return;
  
  // Extract filters from the current dashboard context
  const route = router.currentRoute.value;
  
  // Try to get filters from dashboard context first, fall back to route query
  let from_date, to_date, user;
  
  // Check if we're in a dashboard context with injected filters
  if (dashboardFilters && fromDate && toDate) {
    // We're in dashboard context - use current dashboard filter values
    // These should be reactive and reflect the current UI state
    from_date = fromDate.value ? fromDate.value.split('-').join('-') : null;
    to_date = toDate.value ? toDate.value.split('-').join('-') : null;
    user = dashboardFilters.user; // This should reflect the currently selected user
  } else {
    // We're in route context - use route query parameters
    from_date = route.query.from_date;
    to_date = route.query.to_date;
    user = route.query.user;
  }
  
  // Determine the route to navigate to based on the item's name
  let targetRoute = 'Leads';
  let additionalQueryParams = {};
  
  // Map dashboard item names to their corresponding pages and filters
  if (item.name) {
    switch (item.name.toLowerCase()) {
      case 'total_leads':
        targetRoute = 'Leads';
        break;
      case 'ongoing_deals':
        targetRoute = 'Deals';
        additionalQueryParams.status_type = 'Ongoing';
        break;
      case 'won_deals':
        targetRoute = 'Deals';
        additionalQueryParams.status_type = 'Won';
        break;
      case 'lost_deals':
        targetRoute = 'Deals';
        additionalQueryParams.status_type = 'Lost';
        break;
      case 'converted_leads':
        targetRoute = 'Contacts';
        break;
      default:
        return; // Don't navigate if not in our allowed list
    }
  }
  
  // Build query parameters - include all that are not null/undefined
  const queryParams = {};
  
  if (from_date) {
    queryParams.from_date = from_date;
  }
  if (to_date) {
    queryParams.to_date = to_date;
  }
  // Include user parameter only if it's explicitly set (not undefined)
  // If user is null, we still include it to indicate "no user filter"
  if (user !== undefined) {
    queryParams.user = user;
  }
  
  // Add any additional parameters
  Object.assign(queryParams, additionalQueryParams);
  
  router.push({
    name: targetRoute,
    query: queryParams
  })
}
</script>