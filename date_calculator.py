# -*- coding: UTF-8 -*-


from workflow import Workflow

from date_format_mappings import DATE_MAPPINGS, \
    DEFAULT_WORKFLOW_SETTINGS, \
    DEFAULT_TIME_EXPR, DEFAULT_TIME_RE

from utils import *
from humanfriendly import *


def format_substraction(command, date_format, new_date):

    if command.seconds_to_add or command.minutes_to_add or command.hours_to_add:
        tf = DEFAULT_TIME_EXPR
    else:
        tf = ""

    if command.years_to_add or command.months_to_add or command.weeks_to_add or command.days_to_add:
        df = date_format
    else:
        df = ""

    if tf and df:
        separator = " @ "
    else:
        separator = ""

    return "{new_date}".format(new_date=new_date.strftime(df + separator + tf))


def do_addition(command, date_format):
    date_1 = convert_to_date(command.date_1, command.time_1, date_format)
    # a bit of maths. Use the time delta stuff to get a new
    # date
    new_date = date_1 + relativedelta(
        seconds=int_or_empty(command.seconds_to_add),
        minutes=int_or_empty(command.minutes_to_add),
        hours=int_or_empty(command.hours_to_add),
        days=int_or_empty(command.days_to_add),
        weeks=int_or_empty(command.weeks_to_add),
        months=int_or_empty(command.months_to_add),
        years=int_or_empty(command.years_to_add))

    return format_substraction(command, date_format, new_date)


def do_subtraction(command, date_format):

    date_1 = convert_to_date(command.date_1, command.time_1, date_format)
    date_2 = convert_to_date(command.date_2, command.time_2, date_format)

    seconds_between = abs((date_2 - date_1).total_seconds())

    if (command.years_format or
            command.months_format or
            command.weeks_format or
            command.days_format or
            command.hours_format or
            command.minutes_format or
            command.seconds_format or
            command.long_format):
        return normalised_days(command, date_1, date_2, seconds_between)

    else:

        if command.date_1 or command.date_2:
            return "{days_between}".format(days_between=pluralize(seconds_between / 86400, "day", "days"))
        else:
            return "{hours_between}".format(hours_between=pluralize(seconds_between / 3600, "hour", "hours"))


def do_subtraction_with_options(command, date_format):
    date_1 = convert_to_date(command.date_1, command.time_1, date_format)
    new_date = date_1 - relativedelta(
        seconds=int_or_empty(command.seconds_to_add),
        minutes=int_or_empty(command.minutes_to_add),
        hours=int_or_empty(command.hours_to_add),
        days=int_or_empty(command.days_to_add),
        weeks=int_or_empty(command.weeks_to_add),
        months=int_or_empty(command.months_to_add),
        years=int_or_empty(command.years_to_add))

    return format_substraction(command, date_format, new_date)


def get_week_number(command, date_format):
    date_1 = convert_to_date(command.date_1, command.time_1, date_format)
    try:
        return "week number = {week_number}".format(week_number=date_1.strftime("%V"))
    except ValueError:
        return "Invalid date!"


# This method will return a normalised version of the
# given number of day.
def normalised_days(command, date_1, date_2, seconds_to_normalise):
    # If the user selected long then he wants the full
    # date, so fill in the format before carrying on.
    if command.long_format:

        difference = relativedelta(date_1, date_2)

        if command.date_1 or command.date_2:
            date_string = "{years}, {months}, {days}".format(
                years=pluralize(abs(difference.years), "year", "years"),
                months=pluralize(abs(difference.months), "month", "months"),
                days=pluralize(abs(difference.days), "day", "days"))
        else:
            date_string = ""

        if command.time_1 or command.time_2:
            time_string = "{hours}, {minutes}, {seconds}".format(
                hours=pluralize(abs(difference.hours), "hour", "hours"),
                minutes=pluralize(abs(difference.minutes), "minute", "minutes"),
                seconds=pluralize(abs(difference.seconds), "second", "seconds"))
        else:
            time_string = ""

        ## Do we need a separator, only if there is something that needs separating

        if date_string and time_string:
            separator = ", "
        else:
            separator = ""

        return date_string + separator + time_string

    else:

        seconds_left = seconds_to_normalise
        normalised_string = ""

        if command.years_format:
            years, seconds_left = divmod(seconds_left, 365 * 86400)
            normalised_string += pluralize(int(years), "year", "years")

        if command.months_format:

            if normalised_string:
                normalised_string += ", "

            months, seconds_left = divmod(seconds_left, 30 * 86400)
            normalised_string += pluralize(int(months), "month", "months")

        if command.weeks_format:

            if normalised_string:
                normalised_string += ", "

            weeks, seconds_left = divmod(seconds_left, 7 * 86400)
            normalised_string += pluralize(int(weeks), "week", "weeks")

        if command.days_format:

            if normalised_string:
                normalised_string += ", "

            days, seconds_left = divmod(seconds_left, 86400)
            normalised_string += pluralize(int(days), "day", "days")

        if command.hours_format:

            if normalised_string:
                normalised_string += ", "

            hours, seconds_left = divmod(seconds_left, 3600)
            normalised_string += pluralize(int(hours), "hour", "hours")

        if command.minutes_format:

            if normalised_string:
                normalised_string += ", "

            minutes, seconds_left = divmod(seconds_left, 60)
            normalised_string += pluralize(int(minutes), "minute", "minutes")

        if command.seconds_format:

            if normalised_string:
                normalised_string += ", "

            normalised_string += pluralize(int(seconds_left), "second", "seconds")

        return normalised_string


def main(wf):
    # Here we go!
    args = wf.args

    # Get the date format from the configuration
    key = wf.settings['date-format']

    date_mapping = DATE_MAPPINGS[key]

    grammar = get_date_grammar(date_mapping['regex'], DEFAULT_TIME_RE)

    # If the date format is not valid then the whole thing won't work

    try:

        command = grammar.parseString(args[0])
        # # Now comes the processing bit. Keeping it simple, we'll use a switch statement
        ## Er . . . Python doesn't have one, so no we won't :-)

        if command.operator == '+' and (command.date_1 or command.time_1) and not (
                command.date_2 or command.time_2) and command.options:
            print do_addition(command, date_mapping['date-format'])

        elif command.operator == '-' and (command.date_1 or command.time_1) and (
                command.date_2 or command.time_2) and not command.options:
            print do_subtraction(command, date_mapping['date-format'])

        elif command.operator == '-' and (command.date_1 or command.time_1) and not (
                command.date_2 or command.time_2) and command.options:
            print do_subtraction_with_options(command, date_mapping['date-format'])

        elif command.operator == '^' and command.date_1:
            print get_week_number(command, date_mapping['date-format'])

        else:
            print "Invalid expression"

    except ParseException:
            print "Invalid command"



# ## Python calling routine. Will only run this app if it is the main program
### Otherwise it won't run because it is an included module -- clever!

if __name__ == '__main__':
    workflow = Workflow(default_settings=DEFAULT_WORKFLOW_SETTINGS)
    sys.exit(workflow.run(main))