import itertools as it
import os

import numpy as np

import xlsxwriter


class StimuliFinder:

    XLS_COL = ["left_p", "left_x", "right_p", "right_x"]
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
                 prop_cont_with_loss=0.5,
                 prop_cont_with_loss_each_cond=(0.6, 0.3, 0.1),
                 prop_incongruent=0.5,
                 ):

        """
        :param prop_cont: int range 0-1.
            Probability of a control trial (i.e. trial with a dominant option)
        :param prop_cont_with_loss: int range 0-1.
            Probability that a control trial is inculdes losses
        :param prop_incongruent: int range 0-1.
            Probability for a trial (if not control) to be incongruent
            (i.e. p1 > p2 <=> x2 < x1)
        """

        # Container for proportion of every type of trial
        self.proportion = {
            "control_trials": prop_cont,
            "with_losses": prop_cont_with_loss,
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
        self.xls_row = 1

    @classmethod
    def _create_xls(cls):

        # Create a workbook and add a worksheet.
        os.makedirs(cls.XLS_FOLDER, exist_ok=True)
        workbook = xlsxwriter.Workbook(os.path.join(cls.XLS_FOLDER,
                                                    cls.XLS_NAME))
        worksheet = workbook.add_worksheet()

        for col_idx, title in enumerate(cls.XLS_COL):
            worksheet.write(0, col_idx, title)

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

    def _write(self, **kwargs):

        for k, v in kwargs.items():
            self.worksheet.write(self.xls_row, self.XLS_COL.index(k), v)

        self.xls_row += 1

    def all(self):

        idx = 0

        print("p fixed; x0 positive.")

        x0 = list(it.combinations(self.X_POS, 2))

        for i, j in list(it.product(self.P, x0)):
            print(f"[{idx}] p0 = ({i}, {i}); x0 = {j}")
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1])
            idx += 1

        print("p fixed; x0 negative.")
        x0 = list(it.combinations(self.X_NEG, 2))

        for i, j in list(it.product(self.P, x0)):
            print(f"[{idx}] p0 = ({i}, {i}); x0 = {j}")
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1])
            idx += 1

        print("p fixed; x0 negative vs positive.")

        x0 = list(it.product(self.X_NEG, self.X_POS))

        for i, j in list(it.product(self.P, x0)):
            print(f"[{idx}] p0 = ({i}, {i}); x0 = {j}")
            self._write(left_p=i, right_p=i, left_x=j[0], right_x=j[1])
            idx += 1

        print("x fixed; x0 positive.")

        p = list(it.combinations(self.P, 2))

        for i, j in list(it.product(p, self.X_POS)):
            print(f"[{idx}] p0 = {i}; x0 = ({j}, {j})")
            self._write(left_p=i[0], right_p=i[1], left_x=j, right_x=j)
            idx += 1

        print("x fixed; x0 negative.")

        for i, j in list(it.product(p, self.X_NEG)):
            print(f"[{idx}] p0 = {i}; x0 = ({j}, {j})")
            self._write(left_p=i[0], right_p=i[1], left_x=j, right_x=j)
            idx += 1

        print("congruent positive.")

        x0 = list(it.combinations(self.X_POS, 2))

        for i, j in list(it.product(p, x0)):
            print(f"[{idx}] p0 = {i}; x0 = {j}")
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1])
            idx += 1

        print("congruent negative.")

        x0 = list(it.combinations(self.X_NEG[::-1], 2))

        for i, j in list(it.product(p, x0)):
            print(f"[{idx}] p0 = {i}; x0 = {j}")
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1])
            idx += 1

        print("incongruent positive.")

        x0 = list(it.combinations(self.X_POS[::-1], 2))

        for i, j in list(it.product(p, x0)):
            print(f"[{idx}] p0 = {i}; x0 = {j}")
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1])
            idx += 1

        print("incongruent negative.")

        x0 = list(it.combinations(self.X_NEG, 2))

        for i, j in list(it.product(p, x0)):
            print(f"[{idx}] p0 = {i}; x0 = {j}")
            self._write(left_p=i[0], right_p=i[1], left_x=j[0], right_x=j[1])
            idx += 1

        self.workbook.close()


def main():

    sf = StimuliFinder()

    sf.all()


if __name__ == "__main__":
    main()
