import itertools as it
import os

import numpy as np

import xlsxwriter


class StimuliFinder:

    XLS_NAME = "stimuli.xlsx"
    XLS_FOLDER = "data"

    GAUGE_MAX = 6
    X_MAX = 3

    P = [0.25, 0.5, 0.75, 1]
    X_POS = np.arange(1, 4)
    X_NEG = np.arange(-3, 0)

    SIDES = ["left", "right"]

    def __init__(self,
                 prop_cont=0.5,
                 prop_with_losses=0.5,
                 prop_cont_with_loss_each_cond=(0.6, 0.3, 0.1),
                 prop_incongruent=0.5,
                 ):

        """
        :param prop_cont: float range 0-1.
            Probability of a control trial (i.e. trial with a dominant option)
        :param prop_with_losses: float range 0-1.
            Probability that a trial is inculdes losses
        :param prop_incongruent: float range 0-1.
            Probability for a trial (if not control) to be incongruent
            (i.e. p1 > p2 <=> x2 < x1)
        """

        # Container for proportion of every type of trial
        self.proportion = {
            "control_trials": prop_cont,
            "with_losses": prop_with_losses,
            "incongruent": prop_incongruent,
            "with_loss_per_cond": prop_cont_with_loss_each_cond
        }

        self.conditions = {
            "control": {
                "without_losses":
                    [
                        self.p_fixed_x0_positive,
                        self.x_fixed_x0_positive

                    ],
                "with_losses":
                    [
                        self.p_fixed_x0_negative,
                        self.x_fixed_x0_negative,
                        self.p_fixed_x0_negative_vs_positive
                    ]
            },
            "congruent": {

                "without_losses": self.congruent_positive,
                "with_losses": self.congruent_negative
            },
            "incongruent": {
                "without_losses": self.incongruent_positive,
                "with_losses": self.incongruent_negative
            }
        }

        self.workbook, self.worksheet = self._create_xls()
        self.xls_row = 0

    @classmethod
    def _create_xls(cls):

        # Create a workbook and add a worksheet.
        os.makedirs(cls.XLS_FOLDER, exist_ok=True)
        workbook = xlsxwriter.Workbook(os.path.join(cls.XLS_FOLDER,
                                                    cls.XLS_NAME))
        worksheet = workbook.add_worksheet()

        return workbook, worksheet

    def find(self):

        control = np.random.random() < self.proportion["control_trials"]
        with_losses = np.random.random() < self.proportion["with_losses"]

        if control:
            if with_losses:
                stimuli = np.random.choice(self.conditions["control"]["with_losses"],
                                           p=self.proportion["with_loss_per_cond"])()
            else:
                stimuli = np.random.choice(self.conditions["control"]["without_losses"])()

        else:
            incongruent = np.random.random() < self.proportion["incongruent"]

            if incongruent:
                relevant_conditions = self.conditions["incongruent"]
            else:
                relevant_conditions = self.conditions["congruent"]

            if with_losses:
                stimuli = relevant_conditions["with_losses"]()
            else:
                stimuli = relevant_conditions["without_losses"]()

        return stimuli

    def p_fixed_x0_positive(self):

        print("p fixed; x0 positive.")

        single_p = np.random.choice(self.P)
        x0 = np.random.choice(self.X_POS, size=2, replace=False)

        return self.assign_values(p=[single_p, single_p], x0=x0, x1=[0, 0])

    def p_fixed_x0_negative(self):

        print("p fixed; x0 negative.")

        single_p = np.random.choice(self.P)
        x0 = np.random.choice(self.X_NEG, size=2, replace=False)

        return self.assign_values(p=[single_p, single_p], x0=x0, x1=[0, 0])

    def p_fixed_x0_negative_vs_positive(self):

        print("p fixed; x0 negative vs positive.")

        single_p = np.random.choice(self.P)
        x0 = [np.random.choice(self.X_NEG), np.random.choice(self.X_POS)]

        return self.assign_values(p=[single_p, single_p], x0=x0, x1=[0, 0])

    # def x_fixed(self):
    #
    #     print("x fixed.")
    #
    #     p = np.random.choice(self.P, size=2, replace=False)
    #     single_x0 = np.random.choice(list(self.X_POS) + list(self.X_NEG))
    #
    #     return self.assign_values(p=p, x0=[single_x0, single_x0], x1=[0, 0])

    def x_fixed_x0_positive(self):

        print("x fixed; x0 positive.")

        p = np.random.choice(self.P, size=2, replace=False)
        single_x0 = np.random.choice(self.X_POS)

        return self.assign_values(p=p, x0=[single_x0, single_x0], x1=[0, 0])

    def x_fixed_x0_negative(self):

        print("x fixed; x0 negative.")

        p = np.random.choice(self.P, size=2, replace=False)
        single_x0 = np.random.choice(self.X_NEG)

        return self.assign_values(p=p, x0=[single_x0, single_x0], x1=[0, 0])

    def congruent_positive(self):

        print("congruent positive.")

        p = sorted(np.random.choice(self.P, size=2, replace=False))
        x0 = sorted(np.random.choice(self.X_POS, size=2, replace=False))

        return self.assign_values(p=p, x0=x0, x1=[0, 0])

    def congruent_negative(self):

        print("congruent negative.")

        p = sorted(np.random.choice(self.P, size=2, replace=False))
        x0 = sorted(np.random.choice(self.X_NEG, size=2, replace=False), reverse=True)

        return self.assign_values(p=p, x0=x0, x1=[0, 0])

    def incongruent_positive(self):

        print("incongruent positive.")

        p = sorted(np.random.choice(self.P, size=2, replace=False))
        x0 = sorted(np.random.choice(self.X_POS, size=2, replace=False), reverse=True)

        return self.assign_values(p=p, x0=x0, x1=[0, 0])

    def incongruent_negative(self):

        print("incongruent negative.")

        p = sorted(np.random.choice(self.P, size=2, replace=False))
        x0 = sorted(np.random.choice(self.X_NEG, size=2, replace=False))

        return self.assign_values(p=p, x0=x0, x1=[0, 0])

    def random(self):

        print("Random")
        while True:

            p = np.random.choice(self.P, size=2)
            x0 = np.zeros(2, dtype=int)
            x1 = np.zeros(2, dtype=int)
            x0[0], x1[0] = np.random.choice(list(self.X_NEG) + [0] + list(self.X_POS), size=2, replace=False)
            x0[1], x1[1] = np.random.choice(list(self.X_NEG) + [0] + list(self.X_POS), size=2, replace=False)

            if p[0] == p[1]:

                if x0[0] == x0[1] and x1[0] == x1[1]:
                    pass

                else:
                    break

            elif p[0] == 1 - p[1]:

                if x0[0] == x1[1] and x1[0] == x0[0]:
                    pass

                else:
                    break

            else:
                break

        return self.assign_values(p=p, x0=x0, x1=x1)

    def assign_values(self, p, x0, x1):
        """
        Output something like:
        {
            "left_p": 0,
            "left_x0": 0,
            "left_x1": 0,
            "left_beginning_angle": 0,
            "right_p": 0,
            "right_x0": 0,
            "right_x1": 0,
            "right_beginning_angle": 0
        }

        """

        stimuli_parameters = {}

        idx = np.random.permutation(2)
        for i, side in zip(idx, self.SIDES):
            stimuli_parameters["{}_p".format(side)] = p[i]
            stimuli_parameters["{}_x0".format(side)] = x0[i]
            stimuli_parameters["{}_x1".format(side)] = x1[i]
            stimuli_parameters["{}_beginning_angle".format(side)] = np.random.randint(0, 360)

        return stimuli_parameters

    def _write(self, left_p, right_p, left_x, right_x, lottery_type,
               comment):

        col_value = [
            ('left_p', left_p),
            ('left_x0', left_x),
            ('right_p', right_p),
            ('right_x0', right_x),
            ('lottery_type', lottery_type),
            ('comment', comment),
        ]

        col = [i[0] for i in col_value]

        if self.xls_row == 0:
            for col_idx, title in enumerate(col):
                self.worksheet.write(0, col_idx, title)

            self.xls_row += 1

        for i, (k, v) in enumerate(col_value):
            self.worksheet.write(self.xls_row, i, v)

        print(f"[{self.xls_row}] p0 = ({left_p}, {right_p}); "
              f"x0 = ({left_x}, {right_x}), type={lottery_type}")
        self.xls_row += 1

    def _type_1(self):

        comment = "CONTROL; p fixed / x varies, x0 negative vs positive"
        print(comment)

        x0 = list(it.product(self.X_NEG, self.X_POS))

        for i, j in list(it.product(self.P, x0)):
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1],
                        lottery_type=1, comment=comment)

    def _type_2(self):

        comment = "CONTROL; p fixed / x varies; x0 positive"
        print(comment)

        x0 = list(it.combinations(self.X_POS, 2))

        for i, j in list(it.product(self.P, x0)):
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1],
                        lottery_type=2,
                        comment=comment)

    def _type_3(self):

        comment = "CONTROL; p fixed / x varies; x0 negative"
        print(comment)

        x0 = list(it.combinations(self.X_NEG, 2))

        for i, j in list(it.product(self.P, x0)):
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1],
                        lottery_type=3, comment=comment)

    def _type_4(self):

        comment = "CONTROL; p varies / x fixed; x0 positive"
        print(comment)

        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, self.X_POS)):
            self._write(left_p=i[0], right_p=i[1], left_x=j, right_x=j,
                        lottery_type=4, comment=comment)

    def _type_5(self):

        comment = "CONTROL; p varies / x fixed; x0 negative"
        print(comment)

        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, self.X_NEG)):
            self._write(left_p=i[0], right_p=i[1], left_x=j, right_x=j,
                        lottery_type=5, comment=comment)

    def _type_6(self):

        comment = "INCONGRUENT POS; p varies / x varies; x0 positive"
        print(comment)

        x0 = list(it.combinations(self.X_POS[::-1], 2))
        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, x0)):
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1],
                        lottery_type=6, comment=comment)

    def _type_7(self):

        comment = "INCONGRUENT NEG; p varies / x varies; x0 negative"
        print(comment)

        x0 = list(it.combinations(self.X_NEG, 2))
        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, x0)):
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1],
                        lottery_type=7, comment=comment)

    def _type_8(self):

        comment = "CONGRUENT POS; p varies / x varies; x0 positive."
        print(comment)

        x0 = list(it.combinations(self.X_POS, 2))
        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, x0)):
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1],
                        lottery_type=8, comment=comment)

    def _type_9(self):

        comment = "CONGRUENT NEG; p varies / x varies; x0 negative"
        print(comment)

        x0 = list(it.combinations(self.X_NEG[::-1], 2))
        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, x0)):
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1],
                        lottery_type=9, comment=comment)

    def all(self):

        for i in range(1, 10):
            getattr(self, f'_type_{i}')()

        self.workbook.close()


def main():

    sf = StimuliFinder()

    sf.all()


if __name__ == "__main__":
    main()
