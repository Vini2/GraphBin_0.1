#!/usr/bin/env python3

"""graphbin_MEGAHIT.py: Refined binning of metagenomic contigs using MEGAHIT assembly graphs.

GraphBin is a metagenomic contig binning tool that makes use of the contig 
connectivity information from the assembly graph to bin contigs. It utilizes 
the binning result of an existing binning tool and a label propagation algorithm 
to correct mis-binned contigs and predict the labels of contigs which are 
discarded due to short length.

graphbin_MEGAHIT.py makes use of the assembly graphs produced by MEGAHIT assembler.
"""

import logging
import time

from graphbin.utils.graphbin_Func import graphbin_main
from graphbin.utils.graphbin_Options import PARSER
from graphbin.utils.parsers import get_initial_bin_count
from graphbin.utils.parsers.megahit_parser import (
    parse_graph,
    get_initial_binning_result,
    get_contig_descriptors,
    write_output,
)


__author__ = "Vijini Mallawaarachchi"
__copyright__ = "Copyright 2019-2022, GraphBin Project"
__credits__ = ["Vijini Mallawaarachchi", "Anuradha Wickramarachchi", "Yu Lin"]
__license__ = "BSD-3"
__version__ = "1.6.1"
__maintainer__ = "Vijini Mallawaarachchi"
__email__ = "vijini.mallawaarachchi@anu.edu.au"
__status__ = "Production"


def run(args):
    # Setup logger
    # -----------------------

    logger = logging.getLogger("GraphBin %s" % __version__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    consoleHeader = logging.StreamHandler()
    consoleHeader.setFormatter(formatter)
    consoleHeader.setLevel(logging.INFO)
    logger.addHandler(consoleHeader)

    start_time = time.time()

    assembly_graph_file = args.graph
    contigs_file = args.contigs
    contig_bins_file = args.binned
    output_path = args.output
    prefix = args.prefix
    delimiter = args.delimiter
    max_iteration = args.max_iteration
    diff_threshold = args.diff_threshold
    MIN_BIN_COUNT = 10

    # Setup output path for log file
    # ---------------------------------------------------

    fileHandler = logging.FileHandler(output_path + "/" + prefix + "graphbin.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    logger.info(
        "Welcome to GraphBin: Refined Binning of Metagenomic Contigs using Assembly Graphs."
    )
    logger.info(
        "This version of GraphBin makes use of the assembly graph produced by MEGAHIT which is based on the de Bruijn graph approach."
    )

    logger.info("Assembly graph file: " + assembly_graph_file)
    logger.info("Existing binning output file: " + contig_bins_file)
    logger.info("Final binning output file: " + output_path)
    logger.info("Maximum number of iterations: " + str(max_iteration))
    logger.info("Difference threshold: " + str(diff_threshold))

    logger.info("GraphBin started")

    # Get the number of bins from the initial binning result
    # --------------------------------------------------------

    n_bins, bins_list = get_initial_bin_count(contig_bins_file, delimiter)

    # Get original contig IDs
    # -------------------------------

    original_contigs = get_contig_descriptors(contigs_file)

    # Get assembly graph
    # --------------------

    assembly_graph, graph_to_contig_map, contigs_map, node_count = parse_graph(
        assembly_graph_file, original_contigs
    )

    # Get initial binning result
    # ----------------------------

    bins = get_initial_binning_result(
        n_bins,
        bins_list,
        contig_bins_file,
        contigs_map.inverse,
        graph_to_contig_map.inverse,
        delimiter,
    )

    # Run GraphBin logic
    # -------------------------------------

    final_bins, remove_labels, non_isolated = graphbin_main(
        n_bins,
        bins,
        bins_list,
        assembly_graph,
        node_count,
        diff_threshold,
        max_iteration,
    )

    elapsed_time = time.time() - start_time

    # Print elapsed time for the process
    logger.info("Elapsed time: " + str(elapsed_time) + " seconds")

    # Write result to output file
    # -----------------------------

    write_output(
        output_path,
        prefix,
        final_bins,
        contigs_file,
        graph_to_contig_map,
        bins,
        contigs_map,
        bins_list,
        delimiter,
        node_count,
        remove_labels,
        non_isolated,
    )

    # Exit program
    # --------------

    logger.info("Thank you for using GraphBin! Bye...!")

    logger.removeHandler(fileHandler)
    logger.removeHandler(consoleHeader)


def main():
    # Setup argument parser
    # -----------------------
    ap = PARSER
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
