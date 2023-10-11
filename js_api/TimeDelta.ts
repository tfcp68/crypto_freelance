export default class TimeDelta {
    public static fromNumber(time_delta: number): TimeDelta {
        const seconds_in_month = TimeDelta.__monthsToSeconds(1);
        const months = time_delta / seconds_in_month | 0;
        time_delta -= months * seconds_in_month;

        const seconds_in_week = TimeDelta.__weeksToSeconds(1);
        const weeks = time_delta / seconds_in_week | 0;
        time_delta -= weeks * seconds_in_week;

        const seconds_in_day = TimeDelta.__daysToSeconds(1);
        const days = time_delta / seconds_in_day | 0;
        time_delta -= days * seconds_in_day;

        const seconds_in_hour = TimeDelta.__hoursToSeconds(1);
        const hours = time_delta / seconds_in_hour | 0;
        time_delta -= hours * seconds_in_hour;

        const seconds_in_minute = TimeDelta.__minutesToSeconds(1);
        const minutes = time_delta / seconds_in_minute | 0;
        time_delta -= minutes * seconds_in_minute;

        const seconds = time_delta;

        return new TimeDelta(months, weeks, days, hours, minutes, seconds);
    }

    public constructor(
        readonly months: number = 0,
        readonly weeks: number = 0,
        readonly days: number = 0,
        readonly hours: number = 0,
        readonly minutes: number = 0,
        readonly seconds: number = 0
    ) {}

    public toNumber(): number {
        return TimeDelta.__monthsToSeconds(this.months) +
               TimeDelta.__weeksToSeconds(this.weeks) +
               TimeDelta.__daysToSeconds(this.days) +
               TimeDelta.__hoursToSeconds(this.hours) +
               TimeDelta.__minutesToSeconds(this.minutes) +
               this.seconds;
    }

    private static __minutesToSeconds(minutes: number): number {
        return minutes * 60;
    }

    private static __hoursToSeconds(hours: number): number {
        return hours * this.__minutesToSeconds(60);
    }

    private static __daysToSeconds(days: number): number {
        return days * this.__hoursToSeconds(24);
    }

    private static __weeksToSeconds(weeks: number): number {
        return weeks * this.__daysToSeconds(7);
    }

    private static __monthsToSeconds(months: number): number {
        return months * this.__daysToSeconds(30);
    }
}
