# -*- coding: utf-8 -*-
"""Tree utilities
"""


class TranslationKind(object):
    in_ = 'in'
    out_ = 'out'


def _normalize_branche(branche, node_mapping):
    new_branches = []
    if node_mapping:
        node_id = node_mapping.get('node_id')
        parts = node_id.split('/')
        aliases = node_mapping.get('aliases')
        for aliase in aliases:
            new_branche = parts[:-1]
            new_branche.append(aliase)
            new_branche = '/'.join(new_branche)
            new_branche = branche.replace(node_id, new_branche)
            new_branches.append(new_branche)

    return new_branches


def _get_mapping_for_branche(branche, mapping):
    nor_branche = branche + '/'
    nodes = [node for node in mapping
             if nor_branche.find(node.get('node_id') + '/') >= 0]
    ordered_nodes = sorted(
        nodes, key=lambda e: len(e.get('node_id').split('/')),
        reverse=True)
    return ordered_nodes


def normalize_branche(branche, mapping):
    map_ = _get_mapping_for_branche(branche, mapping)
    branches = []
    for node in map_:
        branches.extend(_normalize_branche(branche, node))

    return list(set(branches))


def normalize_branches_in(branches, mapping):
    result = list(branches)
    for branche in branches:
        branch_result = normalize_branche(branche, mapping)
        if branch_result:
            result.extend(branch_result)
            result.extend(normalize_branches_out(branch_result, mapping))

    return list(set(result))


def normalize_branches_out(branches, mapping):
    new_branches = list(branches)
    for node_mapping in mapping:
        node_id = node_mapping.get('node_id')
        parts = node_id.split('/')
        aliases = node_mapping.get('aliases')
        for aliase in aliases:
            branche_to_replace = parts[:-1]
            branche_to_replace.append(aliase)
            branche_to_replace = '/'.join(branche_to_replace)
            _new_branches = []
            for branche in new_branches:
                if (branche + '/').find(branche_to_replace + '/') >= 0:
                    _new_branches.append(
                        branche.replace(branche_to_replace, node_id))
                else:
                    _new_branches.append(branche)

            new_branches = _new_branches

    return list(set(new_branches))


def normalize_tree(tree, mapping, type_=TranslationKind.out_):
    branches = get_branches(tree)
    if type_ == TranslationKind.out_:
        branches = normalize_branches_out(branches, mapping)
    else:
        branches = normalize_branches_in(branches, mapping)

    return branches_to_tree(branches)


def normalize_keywords_in(keywords, mapping):
    new_keywords = []
    mapping_nodes = {
        node_mapping.get('node_id').split('/')[-1].lower(): node_mapping
        for node_mapping in mapping}
    for keyword in list(keywords):
        new_keyword = [keyword]
        if keyword.lower() in mapping_nodes:
            node_mapping = mapping_nodes[keyword.lower()]
            new_keyword = list(node_mapping.get('aliases'))

        new_keywords.extend(new_keyword)

    return new_keywords


def normalize_keywords_out(keywords, mapping):
    new_keywords = []
    mapping_nodes = {}
    for node_mapping in mapping:
        for alias in node_mapping.get('aliases'):
            mapping_nodes[alias] = node_mapping

    for keyword in list(keywords):
        new_keyword = [keyword]
        if keyword.lower() in mapping_nodes:
            node_mapping = mapping_nodes[keyword.lower()]
            new_keyword = [node_mapping.get('node_id').split('/')[-1]]

        new_keywords.extend(new_keyword)

    return new_keywords


def normalize_keywords(keywords, mapping, type_=TranslationKind.out_):
    if type_ == TranslationKind.in_:
        return normalize_keywords_in(keywords, mapping)
    else:
        return normalize_keywords_out(keywords, mapping)

    return keywords


def node_to_keywords(node_name, children, source):
    new_source = node_name
    if source is not None:
        new_source = source + '/' + node_name

    result = [node_name, new_source]
    path = []
    for child  in children:
        child_keywords, child_path = node_to_keywords(
                          child, children[child], new_source)
        result.extend(child_keywords)
        result.extend(child_path)
        path.extend([node_name + '/' + k for k in child_path])

    if not children:
        path = [node_name]

    return result, path


def tree_to_keywords(tree):
    result = []
    for node in tree:
        node_keywords, node_path = node_to_keywords(node, tree[node], None)
        result.extend(node_keywords)
        result.extend(node_path)

    return list(set(result))


def get_keywords_by_level(tree, root, iskeywords=False):
    keywords = []
    if iskeywords:
        keywords = tree
    else:
        keywords = tree_to_keywords(tree)

    branches = sorted([k.split('/') for k in keywords
                       if k.startswith(root.lower()) or
                          k.startswith(root)],
                      key=lambda e: len(e), reverse=True)
    len_tree = len(branches[0])
    result = {}
    for index in range(len_tree):
        result[index] = []
        for branche in branches:
            if len(branche) > index:
                result[index].append(branche[index])

        result[index] = list(set(result[index]))
    return list(result.values())


def get_tree_nodes_by_level(tree):
    all_nodes = []
    nodes = [(n[0], list(n[1].keys())) for n in tree.items()]
    all_nodes.append(nodes)
    nodes_values = [[(key, value) for value in n.items()]
                    for key, n in list(tree.items())]
    sub_nodes = [item for sublist in nodes_values for item in sublist]
    while sub_nodes:
        nodes = list([(n[0]+'-'+n[1][0], list(n[1][1].keys()))
                     for n in sub_nodes])
        all_nodes.append(nodes)
        nodes_values = [[(origine+'-'+key, value) for value in n.items()]
                        for origine, (key, n) in list([n for n in sub_nodes])]
        sub_nodes = [item for sublist in nodes_values for item in sublist]

    return all_nodes


def merge_nodes(node1_name, children1, node2_name, children2):
    if node1_name != node2_name:
        return {node1_name: children1.copy(),
                node2_name: children2.copy()}

    node = {node1_name: merge_tree(children1, children2)}
    return node


def merge_tree(tree1, tree2, mapping=[]):
    if tree2 and mapping:
        tree2 = normalize_tree(tree2, mapping)

    if not tree1:
        return tree2

    if not tree2:
        return tree1

    result_tree = {}
    merged_nodes = []
    for node in tree1:
        nodes_to_merge = [n for n in tree2
                          if node == n]
        if not nodes_to_merge:
            result_tree.update({node: tree1[node].copy()})
        else:
            node_to_merge = nodes_to_merge[0]
            result_tree.update(merge_nodes(node, tree1[node],
                                           node_to_merge, tree2[node_to_merge]))
            merged_nodes.append(node_to_merge)

    nodes_to_merge = {n: tree2[n] for n in tree2 if n not in merged_nodes}
    result_tree.update(nodes_to_merge)
    return result_tree


def get_branches_node(node_name, children):
    result = []
    for child in children:
        result.extend([node_name + '/' + k for k
                       in get_branches_node(child, children[child])])

    if not children:
        result = [node_name]

    return result


def get_branches(tree):
    result = []
    for node in tree:
        result.extend(get_branches_node(node, tree[node]))

    return result


def get_all_branches(tree):
    branches = get_branches(tree)
    result = []
    for branche in branches:
        result.append(branche)
        parts = branche.split('/')
        while parts:
            parts.pop()
            result.append('/'.join(parts))

    return list(set(result))


def branch_to_tree(branch):
    nodes = branch.split('/')
    nodes.reverse()
    current_node = None
    for node_name in nodes:
        node = {node_name: {}}
        if current_node:
            node[node_name].update(current_node)

        current_node = node

    return current_node


def branches_to_tree(branches):
    branches_nodes = [branch_to_tree(b) for b in branches]

    if not branches_nodes:
        return {}

    current_branch = branches_nodes[0]
    if len(branches_nodes) > 1:
        for branch in branches_nodes[1:]:
            current_branch = merge_tree(current_branch, branch)

    return current_branch


def replace_branche(branch, new_branch, branches):
    return [old_branch.replace(branch, new_branch)
            for old_branch in branches]


def tree_diff(tree1, tree2, mark_diff=''):
    branches1 = get_all_branches(tree1)
    branches2 = get_all_branches(tree2)
    result = []
    for branch in branches2:
        if branch not in branches1:
            result.append(branch)

    if mark_diff:
        diff_result = list(result)
        for branch in result:
            diff_result = replace_branche(
                branch, branch+mark_diff, list(diff_result))

        result = diff_result

    return branches_to_tree(result)


def intersect_nodes(node1_name, children1, node2_name, children2):
    if node1_name != node2_name:
        return {node1_name: children1.copy()}

    node = {node1_name: intersect_tree(children1, children2)}
    return node


def intersect_tree(tree1, tree2):
    if not tree1:
        return tree2

    if not tree2:
        return tree1

    result_tree = {}
    for node in tree1:
        nodes_to_merge = [n for n in tree2
                         if node == n]
        if not nodes_to_merge:
            result_tree.update({node: tree1[node].copy()})
        else:
            node_to_merge = nodes_to_merge[0]
            result_tree.update(intersect_nodes(
                node, tree1[node], node_to_merge, tree2[node_to_merge]))

    return result_tree


def edit_keywords(keywords, newkeyword, tree):
    branches = get_branches(tree)
    new_branches = []
    edited = False
    for branch in branches:
        split = branch.split('/')
        newbranch = branch
        for keyword in keywords:
            if keyword in split:
                result = []
                for item in split:
                    if keyword == item:
                        result.append(newkeyword)
                    else:
                        result.append(item)

                newbranch = '/'.join(result)
                edited = True

        new_branches.append(newbranch)

    if not edited:
        return False

    return branches_to_tree(new_branches)


def tree_len(tree):
    if tree:
        return 1 + max([tree_len(node) for node in tree.values()])
    else:
        return 0


def tree_min_len(tree):
    if tree:
        return 1 + min([tree_min_len(node) for node in tree.values()])
    else:
        return 0
