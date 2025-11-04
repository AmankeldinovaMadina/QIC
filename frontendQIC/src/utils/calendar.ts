/**
 * Utility functions for Google Calendar export (ICS format)
 */

export interface CalendarEvent {
  title: string;
  description?: string;
  location?: string;
  start: Date;
  end: Date;
}

/**
 * Generate ICS file content for Google Calendar
 */
export function generateICS(events: CalendarEvent[], tripTitle: string): string {
  const now = new Date();
  const timestamp = formatICSDate(now);
  
  let ics = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//QIC Travel Planner//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:${tripTitle}
X-WR-TIMEZONE:UTC
`;
  
  events.forEach((event, index) => {
    ics += `BEGIN:VEVENT
UID:${Date.now()}-${index}@qic-travel
DTSTAMP:${timestamp}
DTSTART:${formatICSDate(event.start)}
DTEND:${formatICSDate(event.end)}
SUMMARY:${escapeICS(event.title)}
`;
    
    if (event.description) {
      ics += `DESCRIPTION:${escapeICS(event.description)}
`;
    }
    
    if (event.location) {
      ics += `LOCATION:${escapeICS(event.location)}
`;
    }
    
    ics += `END:VEVENT
`;
  });
  
  ics += `END:VCALENDAR`;
  
  return ics;
}

/**
 * Format date for ICS (UTC format)
 */
function formatICSDate(date: Date): string {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, '0');
  const day = String(date.getUTCDate()).padStart(2, '0');
  const hours = String(date.getUTCHours()).padStart(2, '0');
  const minutes = String(date.getUTCMinutes()).padStart(2, '0');
  const seconds = String(date.getUTCSeconds()).padStart(2, '0');
  
  return `${year}${month}${day}T${hours}${minutes}${seconds}Z`;
}

/**
 * Escape special characters for ICS format
 */
function escapeICS(text: string): string {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '');
}

/**
 * Download ICS file
 */
export function downloadICS(icsContent: string, filename: string = 'trip-calendar.ics'): void {
  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

