#!/usr/bin/env python3

# -*- coding: utf-8 -*-

from Bio import Phylo
from Bio.Phylo import NewickIO  # directly called due to stdout usage
import sys
import logging



def fixname(name):
    if name in mappings:
        return mappings[name]
    else:
        return name

def relabel(clade):
    if clade.name:
        if clade.confidence is not None:
            log.warning('Clade with "confidence value of "%f" got also name "%s". Overwriting.' % (
                clade.name,
                clade.confidence
            ))
        clade.name = fixname(clade.name)
    # fix broken confidence writer when working with PAUP* style files.
    # TreeGraph could not handle confidence behind colons
    # @link http://wiki.christophchamp.com/index.php?title=Newick_phylogenetic_tree_format
    # @link https://en.wikipedia.org/wiki/Newick_format
    # @see Bio.Phylo.NewickIO.Writer#_info_factory
    elif clade.confidence is not None:
        clade.name = str(clade.confidence)
        clade.confidence = None
    if clade.clades:
        for subclade in clade.clades:
            relabel(subclade)

def relabeltree(trees):
    outtrees = []
    for tree in trees:
        if tree.clade:
            relabel(tree.clade)
        outtrees.append(tree)
    return outtrees

def readtrees(treefile):
    return Phylo.parse(treefile, 'newick')

def readmappings(mappingfile):
    mappings = {}
    handle = open(mappingfile)
    if(handle):
        for line in handle:
            line = line.rstrip()
            try:
                code, name = line.split(',', 1)
            except ValueError:
                # todo collect ignorable items
                continue
            if code and name:
                if code not in mappings.values():
                    mappings[code] = name
    return mappings

def printtrees(trees):
    for tree in trees:
        Phylo.draw_ascii(tree)

stdout_handler = logging.StreamHandler(sys.stderr)
handlers = [stdout_handler]
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s - %(message)s]',
    handlers=handlers
)
log = logging.getLogger('LOGGER_NAME')

mappingfile = sys.argv[2]
mappings = readmappings(mappingfile)

treefile = sys.argv[1]
trees = readtrees(treefile)

trees = relabeltree(trees)
#printtees(trees)


NewickIO.write(trees, sys.stdout)