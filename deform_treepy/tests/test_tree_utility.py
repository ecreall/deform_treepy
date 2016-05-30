# -*- coding: utf-8 -*-
"""Tests for text_analyzer utility
"""

from deform_treepy.utilities.tree_utility import (
    tree_to_keywords,
    get_branches,
    merge_tree,
    branches_to_tree,
    get_keywords_by_level,
    intersect_tree,
    normalize_tree)

from deform_treepy.testing import FunctionalTests


class TestTreeUtilityIntegration(FunctionalTests): #pylint: disable=R0904
    """Test Tree Utility integration"""

    def setUp(self):
        super(TestTreeUtilityIntegration, self).setUp()

    def test_tree_to_keywords(self):
        tree = {'Rubrique': {'node1': {'subnode1': {}, 'subnode2': {}}}}
        result = tree_to_keywords(tree)
        self.assertEqual(len(result), 9)
        keywords = ['subnode2', 'Rubrique/node1/subnode2', 'Rubrique/node1',
                    'node1', 'Rubrique/node1/subnode1', 'node1/subnode1',
                    'Rubrique', 'node1/subnode2', 'subnode1']
        for keyword in keywords:
            self.assertIn(keyword, result)

        tree = {'Rubrique': {'node1': {'subnode1': {'subsubnode2': {'level3': {}}}}}}
        result = tree_to_keywords(tree)
        self.assertEqual(len(result), 12)
        keywords = ['Rubrique/node1/subnode1', 'subnode1', 'node1', 'Rubrique',
                   'Rubrique/node1/subnode1/subsubnode2', 'subsubnode2/level3',
                   'subsubnode2', 'Rubrique/node1', 'level3',
                   'subnode1/subsubnode2/level3',
                   'node1/subnode1/subsubnode2/level3',
                   'Rubrique/node1/subnode1/subsubnode2/level3']
        for keyword in keywords:
            self.assertIn(keyword, result)

        tree = {'Rubrique': {'node1': 
                       {'subnode1': 
                                     {'subsubnode2': 
                                                     {'level3': {},
                                                     'level3-2': {}}},
                       'subnode2': {}}}}
        result = tree_to_keywords(tree)
        self.assertEqual(len(result), 20)
        keywords = ['subsubnode2/level3', 'subnode2',
                    'subnode1/subsubnode2/level3-2',
                    'Rubrique/node1/subnode1', 'node1/subnode2',
                    'subnode1/subsubnode2/level3',
                    'Rubrique/node1/subnode1/subsubnode2/level3', 'subnode1',
                    'node1/subnode1/subsubnode2/level3-2',
                    'Rubrique/node1/subnode1/subsubnode2/level3-2',
                    'node1/subnode1/subsubnode2/level3', 'node1',
                    'Rubrique/node1/subnode1/subsubnode2',
                    'subsubnode2', 'level3', 'Rubrique/node1/subnode2',
                    'Rubrique/node1', 'level3-2',
                    'Rubrique', 'subsubnode2/level3-2']
        for keyword in keywords:
            self.assertIn(keyword, result)

    def test_get_branches(self):
        tree = {'Rubrique': {'node1': {'subnode1': {}, 'subnode2': {}}}}
        result = get_branches(tree)
        self.assertEqual(len(result), 2)
        keywords = ['Rubrique/node1/subnode2', 'Rubrique/node1/subnode1']
        for keyword in keywords:
            self.assertIn(keyword, result)

        tree = {'Rubrique': {'node1': {'subnode1': {'subsubnode2':
                {'level3': {}}}}}}
        result = get_branches(tree)
        self.assertEqual(len(result), 1)
        keywords = ['Rubrique/node1/subnode1/subsubnode2/level3']
        for keyword in keywords:
            self.assertIn(keyword, result)

    def test_merge_tree(self):
        tree1 = {'Rubrique': {'node1': {'subnode1': {},
                                        'subnode2': {}}}}
        tree2 = {'Rubrique': {'node2': {'subnode1':
                                   {'subsubnode2': {'level3': {}}}}}}
        result = merge_tree(tree1, tree2)
        result_expected = {
            'Rubrique': {'node1': {'subnode1': {}, 'subnode2': {}},
                         'node2': {'subnode1': {'subsubnode2': {'level3': {}}}}}}
        self.assertEqual(result, result_expected)

        tree1 = {'Rubrique': {'node1': {'subnode1': {},
                                        'subnode2': {}}}}
        tree2 = {'Rubrique': {'node1': {'subnode1':
                      {'subsubnode2': {'level3': {}}}}}}
        result = merge_tree(tree1, tree2)
        result_expected = {
            'Rubrique': {'node1': {'subnode1': {'subsubnode2':
                                                    {'level3': {}}},
                                    'subnode2': {}}}}
        self.assertEqual(result, result_expected)

    def test_branches_to_tree(self):
        branche1 = 'Rubrique/node1/subnode1'
        branche2 = 'Rubrique/node1/subnode2'
        result = branches_to_tree([branche1, branche2])
        result_expected = {'Rubrique': {'node1': {'subnode1': {}, 'subnode2': {}}}}
        self.assertEqual(result, result_expected)
        branche1 = 'Rubrique/node1/subnode1'
        branche2 = 'Rubrique/node1/subnode2'
        branche3 = 'Rubrique/node1/subnode2/subnode3'
        branche4 = 'Rubrique/node1/subnode2/subnode4'
        result = branches_to_tree([branche1, branche2,
                                        branche3, branche4])
        result_expected = {'Rubrique': {'node1': {'subnode1': {},
             'subnode2': {'subnode3': {}, 'subnode4': {}}}}}
        self.assertEqual(result, result_expected)

    def test_get_keywords_by_level(self):
        root = 'Rubrique'
        tree = {root: {'node1': {'subnode1': {}, 'subnode2': {}}}}
        result = get_keywords_by_level(tree, root, iskeywords=False)
        result_expected = [[root], ['node1'], ['subnode2', 'subnode1']]
        self.assertEqual(len(result), len(result_expected))
        for index, level in enumerate(result):
            result_expected_index = result_expected[index]
            self.assertEqual(len(level), len(result_expected_index))
            for keyword in level:
                self.assertIn(keyword, result_expected_index)

        tree = {root: {'node1': {'subnode1': 
                  {'subnode2': {'level3': {}}}}}}
        result = get_keywords_by_level(tree, root, iskeywords=False)
        result_expected = [[root], ['node1'],['subnode1'],['subnode2'], ['level3']]
        self.assertEqual(len(result), len(result_expected))
        for index, level in enumerate(result):
            result_expected_index = result_expected[index]
            self.assertEqual(len(level), len(result_expected_index))
            for keyword in level:
                self.assertIn(keyword, result_expected_index)

        keywords = ['subnode2', 'rubrique/node1/subnode2', 'rubrique/node1',
                    'node1', 'rubrique/node1/subnode1', 'node1/subnode1',
                    'rubrique', 'node1/subnode2', 'subnode1']
        result = get_keywords_by_level(keywords, root, iskeywords=True)
        result_expected = [['rubrique'], ['node1'],['subnode1','subnode2']]
        self.assertEqual(len(result), len(result_expected))
        for index, level in enumerate(result):
            result_expected_index = result_expected[index]
            self.assertEqual(len(level), len(result_expected_index))
            for keyword in level:
                self.assertIn(keyword, result_expected_index)

    def test_intersect_tree(self):
        tree1 = {'Rubrique': {'node1': {'subnode1': {},
                                       'subnode2': {}}}}
        tree2 = {'Rubrique': {'node1': {'subnode1':
                                       {'subsubnode2': {'level3': {}}}}}}

        result = result = intersect_tree(tree1, tree2)
        result_expected = {'Rubrique': {'node1': {'subnode1': {'subsubnode2': 
          {'level3': {}}}, 'subnode2': {}}}}
        self.assertEqual(result, result_expected)

        tree2 = {'Rubrique': {'node2': {'subnode1':
                                   {'subsubnode2': {'level3': {}}}}}}

        result = intersect_tree(tree1, tree2)
        result_expected = tree1
        self.assertEqual(result, result_expected)
        tree1 = []
        tree2 = {'Rubrique': {'node1': {'subnode1':
                                   {'subsubnode2': {'level3': {}}}}}}

        result = intersect_tree(tree1, tree2)
        result_expected = tree2
        self.assertEqual(result, result_expected)

        tree1 = {'Rubrique': {'node1': {'subnode1': {},
                                       'subnode2': {}}}}
        tree2 = []
        result = intersect_tree(tree1, tree2)
        result_expected = tree1
        self.assertEqual(result, result_expected)

    def test_tree_normalizer_in(self):
        tree = {'Rubrique': {'node1': {'subnode1': {},
                                       'subnode2': {}}}}
        mapping = [{'node_id': 'Rubrique/node1', 'aliases': ['node2', 'node3']},
        {'node_id': 'Rubrique/node1/subnode1', 'aliases': ['level3', 'level2']},
        {'node_id': 'Rubrique/node1/subnode2', 'aliases': ['level4', 'level5']}
        ]
        result = normalize_tree(tree, mapping, 'in')
        my_result = {'Rubrique': {'node3': {'subnode1': {}, 'subnode2': {}}, 'node2': {'subnode1': {}, 'subnode2': {}}, 'node1': {'level3': {}, 'level2': {}, 'subnode2': {}, 'subnode1': {}, 'level4': {}, 'level5': {}}}}
        self.assertEqual(result, my_result)

    def test_tree_normalizer_out(self):
        tree = {'Rubrique': {'node1': {'subnode1': {},
                                       'subnode2': {}}}}
        mapping = [{'node_id': 'Rubrique/node1', 'aliases': ['node2', 'node3']},
        {'node_id': 'Rubrique/node1/subnode1', 'aliases': ['level3', 'level2']},
        {'node_id': 'Rubrique/node1/subnode2', 'aliases': ['level4', 'level5']}
        ]
        tree1 = normalize_tree(tree, mapping, 'in')
        result = normalize_tree(tree1, mapping, 'out')
        self.assertEqual(result, tree)
