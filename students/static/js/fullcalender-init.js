document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  if(!calendarEl) return;
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    events: '/events/json/'  // we'll add this endpoint if desired
  });
  calendar.render();
});