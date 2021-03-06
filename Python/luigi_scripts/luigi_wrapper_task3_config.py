#!/usr/bin/env python

import os
from os.path import join as pjoin
import luigi
import cPickle as pickle


def my_function(argument):
    if argument % 2 == 0:
        return "Number is even"
    else:
        msg = "Number: {}; is odd and must be even."
        raise TypeError(msg.format(argument))


class UpperTask1(luigi.Task):

    """Top layer task"""
    out_path = luigi.Parameter(default='')
    out_fname = luigi.Parameter(default='upper1.txt')

    def requires(self):
        return []

    def output(self):
        out_path = self.out_path
        target = luigi.LocalTarget(pjoin(out_path, self.out_fname))
        return {'yo': target}

    def run(self):
        with self.output()['yo'].open('w') as src:
            src.write('Say ')


class UpperTask2(luigi.Task):

    """Top layer task"""
    out_path = luigi.Parameter(default='')
    out_fname = luigi.Parameter(default='upper2.txt')

    def requires(self):
        return []

    def output(self):
        out_path = self.out_path
        target = luigi.LocalTarget(pjoin(out_path, self.out_fname))
        return {'ay': target}

    def run(self):
        with self.output()['ay'].open('w') as src:
            src.write('Say ')


class DoUppers(luigi.WrapperTask):

    """Helper task"""

    out_path = luigi.Parameter()

    def requires(self):
        return {('a', 'b'): {'u1': UpperTask1(self.out_path),
                'u2': UpperTask2(self.out_path)}}


class Combine(luigi.Task):

    """Combine outputs."""

    out_path = luigi.Parameter(default='')
    out_fname = luigi.Parameter(default='greetings.pkl')

    def requires(self):
        return DoUppers(self.out_path)

    def output(self):
        out_path = self.out_path
        target = pjoin(out_path, self.out_fname)
        return luigi.LocalTarget(target)

    def run(self):
        data = {}
        # for key in self.requires().input()[('a', 'b')]:
        #     data[key] = self.requires().input()[('a', 'b')][key].path
        print "requires: ",  self.requires().input()
        print "input: ", self.input()
        for key in self.requires().input()[('a', 'b')]:
            #data[key] = self.input()[('a', 'b')][key].path
            for k, v in self.requires().input()[('a', 'b')][key].items():
                data[key] = v

        #data['upper'] = self.input()
        with self.output().open('w') as src:
            pickle.dump(data, src)


if __name__ == '__main__':
    luigi.run()
