import itertools

from src.lecture import Lecture
from src.read import read
from src.render import save_schedule_img
from src.render import get_schedule_img


# divide the lectures of a group into blocks of lectures by subject
def subject_block(lectures: list[Lecture], subject: str):

    block = []

    for lecture in lectures:
        if lecture.subject == subject:
            block.append(lecture)

    return block


# get the blocks of lectures by subject for all the groups
def subject_lecture_blocks(my_subjects, group_lectures):
    subject_lecture_block = []

    for subject in my_subjects:
        blocks = []

        for lectures in group_lectures.values():
            block = subject_block(lectures, subject)

            # some groups don't have the subject
            if len(block) > 0:
                blocks.append(block)

        # if the subject has a wrong name or doesn't exist
        if len(blocks) > 0:
            subject_lecture_block.append(blocks)
        else:
            raise Exception(
                f"The subject {subject} doesn't exist or is not written well."
            )

    return subject_lecture_block


# generate all the posible valid schedules
def generate_schedules(subject_lecture_blocks):

    # generate all the possible schedules
    unvalidated_shedules = list(itertools.product(*subject_lecture_blocks))

    # list to store the valid schedules
    schedules = []

    for schedule in unvalidated_shedules:
        schedule_lectures = []

        # flatten the schedule
        for block in schedule:
            for lecture in block:
                schedule_lectures.append(lecture)

        # save if the schedule is valid
        if valid_schedule(schedule_lectures):
            schedules.append(schedule_lectures)

    return schedules


# check if the schedule doesn't have two lectures at the same time
def valid_schedule(lectures):
    for l1 in lectures:
        for l2 in lectures:
            if l1 != l2 and l1.day == l2.day and l1.hour == l2.hour:
                return False

    return True


# transform a schedule into a map (matrix of booleans)
def schedule_to_map(schedule):
    schedule_map = [[False for _ in range(6)] for _ in range(5)]

    for lecture in schedule:
        schedule_map[lecture.day][lecture.hour] = True

    return schedule_map


# filter the schedules by the desired conditions
def filter_schedule(
    lecture_map, max_lectures_day=3, max_spaces=1, avoid_single_lectures=False
):

    spaces = 0

    for day in lecture_map:

        num_lectures = day.count(True)
        if num_lectures == 1 and avoid_single_lectures:
            return False

        num_lectures = sum(day)
        current_lecture = 0

        if num_lectures > max_lectures_day:
            return False

        for hour in day:
            if hour:
                current_lecture += 1
            else:
                if current_lecture > 0 and current_lecture < num_lectures:
                    spaces += 1

    if spaces > max_spaces:
        return False

    return True


def save_my_schedules(
    my_subjects,
    group_lectures,
    MAX_LECTURES_DAY=4,
    MAX_WAITING_SPACES=2,
    AVOID_SINGLE_LECTURES=False,
):
    # divide the lectures into blocks by subject
    my_subject_lecture_blocks = subject_lecture_blocks(my_subjects, group_lectures)

    # check if all the subjects have been found
    assert len(my_subjects) == len(
        my_subject_lecture_blocks
    ), "Some subjects were not found."

    # generate the schedules
    schedules = generate_schedules(my_subject_lecture_blocks)

    # filter the schedules
    for schedule in schedules:
        # convert the schedule into a map (speed up calculations)
        schedule_map = schedule_to_map(schedule)

        if filter_schedule(
            schedule_map, MAX_LECTURES_DAY, MAX_WAITING_SPACES, AVOID_SINGLE_LECTURES
        ):
            # save the schedule in the out/ folder
            save_schedule_img(schedule)


if __name__ == "__main__":
    # subjects that I want to study
    my_subjects = [
        "Log. Mat. Discre",
        "Pensa. Creativo",
        "Sist. Operativos",
        "Redes Ordenadores",
        "Prob. Estadist",
        "Proyectos 2",
    ]

    # read the lectures of the groups
    group_lectures = read("data.json")

    # get_schedule_img(group_lectures["INSO2D"]).show()

    # show all the schedules
    # for group in group_lectures:
    #     get_schedule_img(group_lectures[group]).show()

    # save the schedules
    save_my_schedules(my_subjects, group_lectures)
