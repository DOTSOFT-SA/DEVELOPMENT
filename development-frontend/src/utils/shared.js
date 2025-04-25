import {addDays, addWeeks, format, isValid, parseISO, startOfWeek} from "date-fns";
import {el} from "date-fns/locale";

/**
 * Formats a date string into a timestamp-like Greek format.
 * Example: "2024-04-01T16:30:00Z" → "01/04/2024 - 19:30"
 */
export const formatTimestampGreek = (dateString) => {
    if (!dateString) return "-";
    const date = parseISO(dateString);
    return isValid(date)
        ? format(date, "dd/MM/yyyy - HH:mm", {locale: el})
        : "-";
};


/**
 * Converts a given week number into a date range in Greek.
 * If the start date and end date fall in different months, both months are shown.
 * Example:
 *   - Same month: 17-23 Μαρτίου
 *   - Different months: 31 Μαρτίου - 6 Απριλίου
 */
export const formatWeekNumberGreek = (weekNumber) => {
    if (!weekNumber || isNaN(weekNumber) || weekNumber < 1 || weekNumber > 53) return "-";
    // Determine the first Monday of the year to align week calculations
    const currentYear = new Date().getFullYear();
    const firstDayOfYear = new Date(currentYear, 0, 1);
    const firstMonday = startOfWeek(firstDayOfYear, {weekStartsOn: 1});
    // Start of the given week & Start of the next week
    const startDate = addWeeks(firstMonday, weekNumber - 1);
    const nextWeekStart = addWeeks(firstMonday, weekNumber);
    if (!isValid(startDate) || !isValid(nextWeekStart)) return "-";
    // End of the current week is one day before the next week's start
    const endDate = addDays(nextWeekStart, -1);
    if (!isValid(endDate)) return "-";
    // Define the start and end day and month
    const startDay = format(startDate, "d", {locale: el});
    const endDay = format(endDate, "d", {locale: el});
    const startMonth = format(startDate, "MMMM", {locale: el});
    const endMonth = format(endDate, "MMMM", {locale: el});
    // Return format e.g., "31 Μαρτίου - 6 Απριλίου"
    return `${startDay} ${startMonth} - ${endDay} ${endMonth}`;
};

/**
 * Executes an asynchronous request and, if it fails once
 * (e.g. during the very first container warm-up), retries it
 * after the specified delay.  The default is **one** retry
 * after 1 second, but you can override both.
 *
 * @param {() => Promise<any>} requestFn  - the async call (no args)
 * @param {number} retries               - how many extra attempts
 * @param {number} delayMs               - wait between attempts
 */
export const withRetry = async (requestFn, retries = 1, delayMs = 2000) => {
    try {
        return await requestFn();
    } catch (error) {
        if (retries === 0) throw error;          // 0 = no more attempts
        await new Promise(res => setTimeout(res, delayMs));
        return withRetry(requestFn, retries - 1, delayMs);
    }
};
