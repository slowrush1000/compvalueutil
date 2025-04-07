import sys
import argparse
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
import logging


class LoggingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        logging.error(message)
        super().error(message)  # 기본 오류 처리도 수행 (sys.exit(2))


class Node:
    def __init__(self, size):
        self.m_values = [None] * size

    def set_value(self, pos, value):
        if 0 <= pos and pos < len(self.m_values):
            self.m_values[pos] = value

    def get_value(self, pos):
        if 0 <= pos and pos < len(self.m_values):
            return self.m_values[pos]
        else:
            return None

    def get_str(self):
        s = ""
        for i in range(len(self.m_values)):
            if None == self.m_values[i]:
                s += " *"
            else:
                s += f" {self.m_values[i]:e}"
        return s


class Compvalueutil:
    def __init__(self):
        self.m_output_prefix = ""
        self.m_comp_size = 2
        self.m_filenames = []
        self.m_name_positions = []
        self.m_value_positions = []
        self.m_node_dic = {}
        #
        self.m_add_value = False
        self.m_abs_value = False
        self.m_name_case = False
        self.m_hist_x_min_max = [None, None]
        #
        # self.m_argparser = argparse.ArgumentParser(prog="compvalueutil.py")
        self.m_argparser = LoggingArgumentParser()

    def print_usage(self):
        print(f"# compvalueutil usage:")
        print(
            f"% compvalueutil.py output_prefix comp_size 1st_filename 1st_name_pos 1st_value_pos 2nd_filename 2nd_name_pos 2nd_value_pos<...> <-add_value> <-abs_value> <-name_case> <-hist_x_min_max min max>"
        )

    def init_logging(self, args):
        if 6 > len(args):
            exit()
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s:%(levelname)s: %(message)s", filename=f"{args[0]}.log"
        )

    def init_argparser(self):
        self.m_argparser.add_argument("output_prefix")
        self.m_argparser.add_argument("comp_size", type=int)
        self.m_argparser.add_argument("filename_namepos_valuepos", nargs="+")
        self.m_argparser.add_argument("-add_value", action="store_true")
        self.m_argparser.add_argument("-abs_value", action="store_true")
        self.m_argparser.add_argument("-name_case", action="store_true")
        self.m_argparser.add_argument("-hist_x_min_max", nargs=2, type=float)

    def read_args(self, args):
        logging.info(f"# read args start ... {datetime.datetime.now()}")
        arg = self.m_argparser.parse_args(args)
        self.m_output_prefix = arg.output_prefix
        # logging.info(f"{self.m_output_prefix}")
        self.m_comp_size = arg.comp_size
        # logging.info(f"{self.m_comp_size}")
        if 0 != (len(arg.filename_namepos_valuepos) % 3):
            logging.info(f"{arg.filename_namepos_valuepos}")
            self.m_argparser.error("Expected filename followed by name pos and value pos")
            exit()
        i = 0
        while i < len(arg.filename_namepos_valuepos):
            if i + 2 >= len(arg.filename_namepos_valuepos):
                self.m_argparser.error("name pos and value pos must be integers")
            self.m_filenames.append(arg.filename_namepos_valuepos[i])
            try:
                self.m_name_positions.append(int(arg.filename_namepos_valuepos[i + 1]))
                self.m_value_positions.append(int(arg.filename_namepos_valuepos[i + 2]))
                i += 3
            except ValueError:
                self.m_argparser.error("name pos and value pos must be integers")
        self.m_add_value = arg.add_value
        self.m_abs_value = arg.abs_value
        self.m_name_case = arg.name_case
        self.m_hist_x_min_max = arg.hist_x_min_max
        logging.info(f"# read args end ... {datetime.datetime.now()}")

    def print_inputs(self):
        logging.info(f"# logging.info inputs start ... {datetime.datetime.now()}")
        logging.info(f"output prefix       : {self.m_output_prefix}")
        logging.info(f"comp size           : {self.m_comp_size}")
        for i in range(self.m_comp_size):
            logging.info(f"{i}th filename      : {self.m_filenames[i]}")
            logging.info(f"{i}th name pos      : {self.m_name_positions[i]}")
            logging.info(f"{i}th value pos     : {self.m_value_positions[i]}")
        logging.info(f"add_value           : {self.m_add_value}")
        logging.info(f"abs_value           : {self.m_abs_value}")
        logging.info(f"name_case           : {self.m_name_case}")
        logging.info(f"hist x min/max      : {self.m_hist_x_min_max[0]} {self.m_hist_x_min_max[1]}")
        logging.info(f"# logging.info inputs end ... {datetime.datetime.now()}")

    def read_files(self):
        logging.info(f"# read files start ... {datetime.datetime.now()}")
        for i in range(self.m_comp_size):
            self.read_file(self.m_filenames[i], i)
        logging.info(f"# read files end ... {datetime.datetime.now()}")

    def read_file(self, filename, i):
        logging.info(f"# read file({filename}) start ... {datetime.datetime.now()}")
        max_pos = self.get_max_pos(i)
        f = open(filename, "rt")
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            if "#" == line[0] or "*" == line[0]:
                continue
            tokens = line.split()
            if max_pos >= len(tokens):
                continue
            name = tokens[self.m_name_positions[i]]
            if False == self.m_name_case:
                name = name.lower()
            value = float(tokens[self.m_value_positions[i]])
            if True == self.m_abs_value:
                value = math.fabs(value)
            #
            if not name in self.m_node_dic:
                node = Node(self.m_comp_size)
                node.set_value(i, value)
                # logging.info(f"#debug-1 {node.m_values}")
                self.m_node_dic[name] = node
            else:
                node = self.m_node_dic[name]
                # logging.info(f"#debug-2 {node.m_values}")
                if None == node.get_value(i):
                    node.set_value(i, value)
                else:
                    value_1 = node.get_value(i)
                    node.set_value(i, value + value_1)
        f.close()
        logging.info(f"# read file({filename}) end ... {datetime.datetime.now()}")

    def print_statistics_all(self):
        logging.info(f"# logging.info statistics all start ... {datetime.datetime.now()}")
        for i in range(self.m_comp_size):
            self.print_statistics(i)
        logging.info(f"# logging.info statistics all end ... {datetime.datetime.now()}")

    def print_statistics(self, i):
        logging.info(f"# logging.info statistics({self.m_filenames[i]}) start ... {datetime.datetime.now()}")
        #
        values = []
        names = []
        for name in self.m_node_dic:
            node = self.m_node_dic[name]
            if None != node.get_value(i):
                values.append(node.get_value(i))
                names.append(name)
        #
        array = np.array(values)
        self.print_statistics_array(f"{i}th", array, names)
        #
        logging.info(f"# logging.info statistics({self.m_filenames[i]}) end ... {datetime.datetime.now()}")

    def compare_all(self):
        logging.info(f"# compare all start ... {datetime.datetime.now()}")
        for i in range(1, self.m_comp_size):
            self.compare(i)
        logging.info(f"# compare all end ... {datetime.datetime.now()}")

    def compare(self, i):
        logging.info(f"# compare 0 vs {i} start ... {datetime.datetime.now()}")
        #
        names = []
        values_0th = []
        values_nth = []
        for name in self.m_node_dic:
            node = self.m_node_dic[name]
            if None != node.get_value(0) and None != node.get_value(i):
                names.append(name)
                values_0th.append(node.get_value(0))
                values_nth.append(node.get_value(i))
        #
        array_0th = np.array(values_0th)
        array_nth = np.array(values_nth)
        array_diff = array_nth - array_0th
        array_diff_percentage = (array_nth - array_0th) / array_0th * 100.0
        #
        self.print_statistics_array("diff", array_diff, names)
        self.print_statistics_array("diff_percentage", array_diff_percentage, names)
        #
        self.write_scatter_plot(array_0th, array_nth, i)
        self.write_histogram_plot(array_diff, i)
        #
        logging.info(f"# compare 0 vs {i} end ... {datetime.datetime.now()}")

    def write_scatter_plot(self, array_0th, array_nth, i):
        logging.info(f"# write scatter plot(0th vs {i}th) start ... {datetime.datetime.now()}")
        plt.figure(figsize=(8, 6))
        plt.scatter(array_0th, array_nth)
        min_value = np.min(array_0th)
        max_value = np.max(array_0th)
        max_value_lower = max_value * 0.9
        max_value_upper = max_value * 1.1
        # logging.info(f"#debug-1 {min_value} {max_value} {max_value_lower} {max_value_upper}")
        array_0th_ceneter_x = np.array([min_value, max_value])
        array_0th_center_bound_y = np.array([min_value, max_value])
        array_0th_lower_bound_y = np.array([min_value, max_value_lower])
        array_0th_upper_bound_y = np.array([min_value, max_value_upper])
        plt.plot(array_0th_ceneter_x, array_0th_center_bound_y, color="black", linestyle="--")
        plt.plot(array_0th_ceneter_x, array_0th_lower_bound_y, color="black", linestyle=":")
        plt.plot(array_0th_ceneter_x, array_0th_upper_bound_y, color="black", linestyle=":")
        plt.scatter(array_0th, array_nth)
        plt.xlabel(f"{self.m_filenames[0]}")
        plt.ylabel(f"{self.m_filenames[i]}")
        plt.title(f"0th vs {i}th scatter plot(+-10%)")
        # plt.colorbar(label="color level")
        plt.grid(True)
        png_filename = f"{self.m_output_prefix}.{i}th.scatter.plot.png"
        plt.savefig(f"{png_filename}")
        plt.close()
        logging.info(f"# write scatter plot(0th vs {i}th) start ... {datetime.datetime.now()}")

    def write_histogram_plot(self, array_diff, i):
        logging.info(f"# write histogram plot(0th vs {i}th) start ... {datetime.datetime.now()}")
        plt.figure(figsize=(8, 6))
        if None != self.m_hist_x_min_max and None != self.m_hist_x_min_max[1]:
            plt.hist(array_diff, bins=50, range=(self.m_hist_x_min_max[0], self.m_hist_x_min_max[1]))
        else:
            plt.hist(array_diff, bins=50)
        plt.xlabel(f"{i}th - 0th")
        png_filename = f"{self.m_output_prefix}.{i}th.histogram.plot.png"
        plt.savefig(f"{png_filename}")
        logging.info(f"# write histogram plot(0th vs {i}th) end ... {datetime.datetime.now()}")

    def print_statistics_array(self, head_msg, array, names):
        logging.info(f"{head_msg} size   : {np.size(array)}")
        logging.info(f"{head_msg} avg    : {np.mean(array)}")
        logging.info(f"{head_msg} median : {np.median(array)}")
        min_index = np.argmin(array)
        max_index = np.argmax(array)
        logging.info(f"{head_msg} min    : {np.min(array)} {names[min_index]}")
        logging.info(f"{head_msg} max    : {np.max(array)} {names[max_index]}")
        logging.info(f"{head_msg} std    : {np.std(array)}")
        logging.info(f"{head_msg} var    : {np.var(array)}")

    def get_max_pos(self, pos):
        return max(self.m_name_positions[pos], self.m_value_positions[pos])

    def print_node_dic(self, size=10):
        logging.info(f"# logging.info node dic start ... {datetime.datetime.now()}")
        count = 0
        for name in self.m_node_dic:
            if count > size:
                logging.info(f"because count({count}) is more than size({size}), print_node_dic is halted.")
                break
            node = self.m_node_dic[name]
            logging.info(f"{name} {node.get_str()}")
            count += 1
        logging.info(f"# logging.info node dic end ... {datetime.datetime.now()}")

    def run(self, args):
        self.init_logging(args)
        logging.info(f"# compvalueutil.py start ... {datetime.datetime.now()}")
        self.init_argparser()
        self.read_args(args)
        self.print_inputs()
        self.read_files()
        self.print_node_dic()
        self.print_statistics_all()
        self.compare_all()
        logging.info(f"# compvalueutil.py end ... {datetime.datetime.now()}")


def main(args):
    my_compvalueutil = Compvalueutil()
    my_compvalueutil.run(args)


if __name__ == "__main__":
    main(sys.argv[1:])
