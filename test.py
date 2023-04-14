from models.answers import *
from models.poll import *

p = PollSchema(
    name="Test Poll Schema",
    plots=[
        BarPlot(
            name="Bar Plot",
            questions=[
                SelectorQuestion(
                    label="Selector Question 1",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=2,
                    max_checked=3,
                ),
                SelectorQuestion(
                    label="Selector Question 2",
                    options=[
                        Option(label="Option 1"),
                        Option(
                            label="Option 2",
                            image="https://i.stack.imgur.com/ajwm5.png",
                        ),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=1,
                    max_checked=1,
                ),
                SelectorQuestion(
                    label="Selector Question 3",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=1,
                    max_checked=None,
                ),
            ],
        ),
        PiePlot(
            name="Pie Plot",
            questions=[
                SliderQuestion(
                    label="Slider Question 1",
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(
                            label="Option 3",
                            image="https://i.stack.imgur.com/ajwm5.png",
                        ),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_value=1,
                    max_value=10,
                ),
                SliderQuestion(
                    label="Slider Question 2",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_value=5,
                    max_value=10,
                ),
            ],
        ),
        DoughnutPlot(
            name="Doughnut Plot",
            questions=[
                SliderQuestion(
                    label="Slider Question 1",
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(
                            label="Option 3",
                            image="https://i.stack.imgur.com/ajwm5.png",
                        ),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_value=1,
                    max_value=10,
                ),
                SliderQuestion(
                    label="Slider Question 2",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_value=5,
                    max_value=10,
                ),
            ],
        ),
        RadarPlot(
            name="Bar Plot",
            questions=[
                TopListQuestion(
                    label="Top List Question 1",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_ranks=2,
                    max_ranks=3,
                ),
                TopListQuestion(
                    label="Top List Question 2",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_ranks=3,
                    max_ranks=3,
                ),
                TopListQuestion(
                    label="Top List Question 3",
                    options=[
                        Option(label="Option 1"),
                        Option(
                            label="Option 2",
                            image="https://i.stack.imgur.com/ajwm5.png",
                        ),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_ranks=1,
                    max_ranks=None,
                ),
            ],
        ),
        AreaPlot(
            name="Area Plot",
            questions=[
                SelectorQuestion(
                    label="Selector Question 1",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=2,
                    max_checked=3,
                ),
                SelectorQuestion(
                    label="Selector Question 2",
                    options=[
                        Option(label="Option 1"),
                        Option(
                            label="Option 2",
                            image="https://i.stack.imgur.com/ajwm5.png",
                        ),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=1,
                    max_checked=1,
                ),
                SelectorQuestion(
                    label="Selector Question 3",
                    hide_results=True,
                    options=[
                        Option(label="Option 1"),
                        Option(label="Option 2"),
                        Option(label="Option 3"),
                        Option(label="Option 4"),
                        Option(label="Option 5"),
                    ],
                    min_checked=1,
                    max_checked=None,
                ),
            ],
        ),
        WordCloudPlot(
            name="Word Cloud Plot",
            questions=[
                TextQuestion(
                    label="Text Question 1",
                    description="Description text",
                    image="https://i.stack.imgur.com/ajwm5.png",
                    min_length=5,
                    max_length=10,
                ),
                TextQuestion(
                    label="Text Question 2",
                    max_length=10,
                ),
                TextQuestion(
                    label="Text Question 3",
                    min_length=5,
                ),
                TextQuestion(
                    label="Text Question 4",
                ),
            ],
        ),
    ],
)

# p1
## q1
v1 = SelectorValue(
    question_id=p.plots[0].questions[0].question_id,
    selected={0, 2},
)
v2 = SelectorValue(
    question_id=p.plots[0].questions[0].question_id,
    selected={0, 2, 4},
)

## q2
v3 = SelectorValue(
    question_id=p.plots[0].questions[1].question_id,
    selected={1},
)

## q3
v4 = SelectorValue(
    question_id=p.plots[0].questions[2].question_id,
    selected={1},
)
v5 = SelectorValue(
    question_id=p.plots[0].questions[2].question_id,
    selected={0, 1, 2, 3, 4},
)


# p2
## q1
v6 = SliderValue(
    question_id=p.plots[1].questions[0].question_id,
    sliders=[10, 8, 6, 4, 2],
)

## q2
v7 = SliderValue(
    question_id=p.plots[1].questions[1].question_id,
    sliders=[10, 9, 8, 7, 6],
)


# p3
## q1
v8 = SliderValue(
    question_id=p.plots[2].questions[0].question_id,
    sliders=[10, 8, 6, 4, 2],
)

## q2
v9 = SliderValue(
    question_id=p.plots[2].questions[1].question_id,
    sliders=[10, 9, 8, 7, 6],
)


# p4
## q1
v10 = TopListValue(
    question_id=p.plots[3].questions[0].question_id,
    ranks=[4, 2],
)
v11 = TopListValue(
    question_id=p.plots[3].questions[0].question_id,
    ranks=[4, 2, 3],
)

## q2
v12 = TopListValue(
    question_id=p.plots[3].questions[1].question_id,
    ranks=[4, 2, 3],
)

## q3
v13 = TopListValue(
    question_id=p.plots[3].questions[2].question_id,
    ranks=[4],
)
v14 = TopListValue(
    question_id=p.plots[3].questions[2].question_id,
    ranks=[4, 3, 2, 1, 0],
)


# p5
## q1
v15 = SelectorValue(
    question_id=p.plots[4].questions[0].question_id,
    selected={0, 2},
)
v16 = SelectorValue(
    question_id=p.plots[4].questions[0].question_id,
    selected={0, 2, 4},
)

## q2
v17 = SelectorValue(
    question_id=p.plots[4].questions[1].question_id,
    selected={1},
)

## q3
v18 = SelectorValue(
    question_id=p.plots[4].questions[2].question_id,
    selected={1},
)
v19 = SelectorValue(
    question_id=p.plots[4].questions[2].question_id,
    selected={0, 1, 2, 3, 4},
)


# p6
## q1
v20 = TextValue(
    question_id=p.plots[5].questions[0].question_id,
    text="12345",
)
v21 = TextValue(
    question_id=p.plots[5].questions[0].question_id,
    text="123567890",
)

## q2
v22 = TextValue(
    question_id=p.plots[5].questions[1].question_id,
    text="",
)

## q3
v23 = TextValue(
    question_id=p.plots[5].questions[2].question_id,
    text="1235678901234567890",
)

## q4
v23 = TextValue(
    question_id=p.plots[5].questions[3].question_id,
    text="1235678901234567890",
)
v24 = TextValue(
    question_id=p.plots[5].questions[3].question_id,
    text="",
)

print(locals()[input("name -> ")].json())
