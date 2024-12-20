import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
import logging
from ..utils.general_functions import calculate_angle_difference, calculate_angle


def find_predecessors_graph(
    from_node_ids: np.array,
    to_node_ids: np.array,
    edge_ids: np.array,
    node_id: int,
    border_node_ids: np.array = None,
    pred_nodes: list = [],
    pred_edges: list = [],
):
    """
    Find predecessors within graph for specified node_id.

    Note: recursive function!
    """
    pred = from_node_ids[np.where(to_node_ids == node_id)]
    edge = edge_ids[np.where(to_node_ids == node_id)]
    for i in range(pred.shape[0]):
        p = pred[i]
        e = edge[i]
        pred_edges = pred_edges + [e]
        if p not in pred_nodes:
            pred_nodes = pred_nodes + [int(p)]
            if border_node_ids is None or p not in border_node_ids:
                pred_nodes, pred_edges = find_predecessors_graph(
                    from_node_ids,
                    to_node_ids,
                    edge_ids,
                    p,
                    border_node_ids,
                    pred_nodes,
                    pred_edges,
                )
    return pred_nodes, pred_edges


def find_predecessors_graph_with_splits(
    from_node_ids,
    to_node_ids,
    edge_ids,
    node_id,
    border_node_ids=None,
    split_node_edge_ids=None,
    split_node_edge_ids2=None,
    pred_nodes=[],
    pred_edges=[],
    new_outflow_nodes=[]
):
    """
    Find predecessors within graph for specified node_id.

    Note: recursive function!
    """
    pred_node = from_node_ids[np.where(to_node_ids == node_id)]
    pred_edge = edge_ids[np.where(to_node_ids == node_id)]
    # print(pred_node)
    # print(pred_edge)
    # print(split_node_edge_ids)
    # print(split_node_edge_ids2)

    for i in range(pred_node.shape[0]):
        p = pred_node[i]
        e = pred_edge[i]
        # print("-----------")
        # print(previous_p)
        # print(p, e)
        if (
            split_node_edge_ids2 is not None
            and node_id in split_node_edge_ids2
            and split_node_edge_ids2[node_id] != e
        ):  
            # print("new_outflow_node", e)
            # print(p)
            # print(previous_p)
            # print(split_node_edge_ids2[int(previous_p)])
            new_outflow_nodes = new_outflow_nodes + [int(node_id)]
            # print(f"{new_outflow_nodes=}")
            continue
        # print("previous_p not in splits or e in splits")
        # print(f"{p} = {split_node_edge_ids2[p]}")
        pred_edges = pred_edges + [e]
        # print(f"{pred_edges=}")
        if p not in pred_nodes:
            pred_nodes = pred_nodes + [int(p)]
            if border_node_ids is None or p not in border_node_ids:
                if (
                    split_node_edge_ids is None
                    or p not in split_node_edge_ids
                    or split_node_edge_ids[p] == e
                ):
                    pred_nodes, pred_edges, new_outflow_nodes = find_predecessors_graph_with_splits(
                        from_node_ids,
                        to_node_ids,
                        edge_ids,
                        p,
                        border_node_ids,
                        split_node_edge_ids,
                        split_node_edge_ids2,
                        pred_nodes,
                        pred_edges,
                        new_outflow_nodes
                    )
    return pred_nodes, pred_edges, new_outflow_nodes


def accumulate_values_graph(
    from_node_ids,
    to_node_ids,
    node_ids,
    edge_ids,
    values_node_ids,
    values_nodes,
    values_edge_ids,
    values_edges,
    border_node_ids=None,
    itself=False,
    direction="upstream",
    decimals=None,
):
    """Calculate for all node_ids the accumulated values of all predecessors with values."""
    len_node_ids = np.shape(node_ids)[0]
    results_nodes = np.zeros(np.shape(node_ids))
    results_edges = np.zeros(np.shape(node_ids))
    logging.info(f"accumulate values using graph for {len(node_ids)} node(s)")
    for i in range(node_ids.shape[0]):
        print(f" * {i+1}/{len_node_ids} ({(i+1)/len(node_ids):.2%})", end="\r")
        node_id = node_ids[i]
        if direction == "upstream":
            pred_nodes, pred_edges = find_predecessors_graph(
                from_node_ids,
                to_node_ids,
                edge_ids,
                node_id,
                border_node_ids,
                np.array([]),
            )
        else:
            pred_nodes, pred_edges = find_predecessors_graph(
                to_node_ids,
                from_node_ids,
                edge_ids,
                node_id,
                border_node_ids,
                np.array([]),
            )
        if itself:
            pred_nodes = np.append(pred_nodes, node_id)
        pred_nodes_sum = np.sum(
            values_nodes[np.searchsorted(values_node_ids, pred_nodes)]
        )
        pred_edges_sum = np.sum(
            values_edges[np.searchsorted(values_edge_ids, pred_edges)]
        )
        if decimals is None:
            results_nodes[i] = pred_nodes_sum
            results_edges[i] = pred_edges_sum
        else:
            results_nodes[i] = np.round(pred_nodes_sum, decimals=decimals)
            results_edges[i] = np.round(pred_edges_sum, decimals=decimals)
    return results_nodes, results_edges


def find_node_edge_ids_in_directed_graph(
    from_node_ids,
    to_node_ids,
    edge_ids,
    node_ids,
    search_node_ids,
    search_edge_ids,
    border_node_ids=None,
    direction="upstream",
    split_points=None,
    set_logging=False,
    order_first=False,
):
    len_node_ids = np.shape(node_ids)[0]
    results_nodes = []
    results_edges = []
    if set_logging:
        logging.debug(
            f"    - find {direction} nodes/edges for {len(node_ids)}/{len(search_node_ids)} nodes"
        )
    search_direction = "upstream" if direction == "downstream" else "downstream"
    opposite_direction = "downstream" if direction == "downstream" else "upstream"
    if isinstance(node_ids, list):
        node_ids = np.array(node_ids)

    new_outflow_nodes = []
    if split_points is None:
        for i in range(node_ids.shape[0]):
            # print(f" * {i+1}/{len_node_ids} ({(i+1)/len(node_ids):.2%})")
            node_id = node_ids[i]
            if direction == "upstream":
                pred_nodes, pred_edges = find_predecessors_graph(
                    from_node_ids, to_node_ids, edge_ids, node_id, border_node_ids, []
                )
            else:
                pred_nodes, pred_edges = find_predecessors_graph(
                    to_node_ids, from_node_ids, edge_ids, node_id, border_node_ids, []
                )
            results_nodes = results_nodes + [[
                p for p in pred_nodes if p in search_node_ids
            ]]
            results_edges = results_edges + [[
                p for p in pred_edges if p in search_edge_ids
            ]]
    else:
        split_node_edge_ids = split_points.set_index("nodeID")[
            f"selected_{search_direction}_edge"
        ].to_dict()
        split_node_edge_ids2 = split_points.set_index("nodeID")[
            f"selected_{opposite_direction}_edge"
        ].to_dict()

        split_node_edge_ids = {
            k: v for k, v in split_node_edge_ids.items() if v not in [None, ""]
        }
        split_node_edge_ids2 = {
            k: v for k, v in split_node_edge_ids2.items() if v not in [None, ""]
        }

        for i in range(node_ids.shape[0]):
            # print(f" * {i+1}/{len_node_ids} ({(i+1)/len(node_ids):.2%})", end="\r")
            node_id = node_ids[i]
            if direction == "upstream":
                pred_nodes, pred_edges, new_outflow_nodes = find_predecessors_graph_with_splits(
                    from_node_ids,
                    to_node_ids,
                    edge_ids,
                    node_id,
                    border_node_ids,
                    split_node_edge_ids if not order_first else None,
                    split_node_edge_ids2,
                    [],
                    [],
                )
            else:
                pred_nodes, pred_edges, new_outflow_nodes = find_predecessors_graph_with_splits(
                    to_node_ids,
                    from_node_ids,
                    edge_ids,
                    node_id,
                    border_node_ids,
                    split_node_edge_ids2,
                    split_node_edge_ids if not order_first else None,
                    [],
                    [],
                )
            results_nodes = results_nodes + [[
                p for p in pred_nodes if p in search_node_ids
            ]]
            results_edges = results_edges + [[
                p for p in pred_edges if p in search_edge_ids
            ]]
    return results_nodes, results_edges, new_outflow_nodes


def find_nodes_edges_for_direction(
    nodes: gpd.GeoDataFrame,
    edges: gpd.GeoDataFrame,
    node_ids: list,
    border_node_ids: list = None,
    direction: str = "upstream",
    split_points: gpd.GeoDataFrame = None,
    order_first: bool = False
):
    nodes_direction, edges_direction, new_outflow_nodes = find_node_edge_ids_in_directed_graph(
        from_node_ids=edges.node_start.to_numpy(),
        to_node_ids=edges.node_end.to_numpy(),
        edge_ids=edges.code.to_numpy(),
        node_ids=node_ids,
        search_node_ids=nodes.nodeID.to_numpy(),
        search_edge_ids=edges.code.to_numpy(),
        border_node_ids=border_node_ids,
        direction=direction,
        split_points=split_points,
        order_first=order_first
    )
    for node_id, node_direction, edge_direction in zip(node_ids, nodes_direction, edges_direction):
        nodes[f"{direction}_node_{node_id}"] = False
        nodes.loc[nodes["nodeID"].isin(node_direction), f"{direction}_node_{node_id}"] = True
        edges[f"{direction}_node_{node_id}"] = False
        edges.loc[edges["code"].isin(edge_direction), f"{direction}_node_{node_id}"] = True
    return nodes, edges, new_outflow_nodes


def calculate_angles_of_edges_at_nodes(
    nodes: gpd.GeoDataFrame, 
    edges: gpd.GeoDataFrame,
    nodes_id_column: str = "nodeID",
):
    edges["upstream_angle"] = edges["geometry"].apply(
        lambda x: calculate_angle(x, "upstream").round(2)
    )
    edges["downstream_angle"] = edges["geometry"].apply(
        lambda x: calculate_angle(x, "downstream").round(2)
    )
    for direction, opp_direction in zip(["upstream", "downstream"], ["downstream", "upstream"]):
        node_end = "node_end" if direction == "upstream" else "node_start"
        nodes[f"{direction}_angles"] = (
            nodes.merge(
                edges[[node_end, f"{opp_direction}_angle"]].rename(columns={node_end: nodes_id_column}),
                how="left",
                on=nodes_id_column,
            )
            .groupby(nodes_id_column)
            .agg({f"{opp_direction}_angle": list})
        )
        nodes[f"{direction}_angles"] = nodes[f"{direction}_angles"].apply(
            lambda x: ",".join([str(a) for a in x]) if ~(isinstance(x[0], float) and np.isnan(x[0])) else ",".join([])
        )
    return nodes, edges


def select_downstream_upstream_edges(nodes, min_difference_angle: str = 20.0):

    def select_downstream_upstream_edges_per_node(x, min_difference_angle: str = 20.0):
        upstream_edges = x["upstream_edges"] = [
            a for a in x["upstream_edges"].split(",") if a != ""
        ]
        downstream_edges = x["downstream_edges"] = [
            a for a in x["downstream_edges"].split(",") if a != ""
        ]
        upstream_angles = x["upstream_angles"] = [
            float(a) for a in x["upstream_angles"].split(",") if a != ""
        ]
        downstream_angles = x["downstream_angles"] = [
            float(a) for a in x["downstream_angles"].split(",") if a != ""
        ]
        
        angle_differences = [
            [round(abs(au - ad), 2) for ad in downstream_angles] for au in upstream_angles
        ]
        smallest_angle1 = None
        smallest_angle2 = None
        selected_upstream_edge = None
        selected_downstream_edge = None
        iteration = 0

        for upstream_edge, upstream_angle_differences in zip(
            upstream_edges, angle_differences
        ):
            for downstream_edge, angle_difference in zip(
                downstream_edges, upstream_angle_differences
            ):
                iteration = iteration + 1
                if smallest_angle1 is None or angle_difference < smallest_angle1:
                    smallest_angle2 = smallest_angle1
                    smallest_angle1 = angle_difference
                    selected_upstream_edge = upstream_edge
                    selected_downstream_edge = downstream_edge
                elif smallest_angle2 is None or angle_difference < smallest_angle2:
                    smallest_angle2 = angle_difference

        x["selected_upstream_edge"] = None
        x["selected_downstream_edge"] = None
        if (
            smallest_angle2 is None
            or smallest_angle1 < smallest_angle2 - min_difference_angle
        ):
            x["selected_upstream_edge"] = selected_upstream_edge
            x["selected_downstream_edge"] = selected_downstream_edge

        if len(x["downstream_edges"]) == 1:
            x["selected_downstream_edge"] = x["downstream_edges"][0]
        if len(x["upstream_edges"]) == 1:
            x["selected_upstream_edge"] = x["upstream_edges"][0]
        
        return x

    nodes = nodes.apply(
        lambda x: select_downstream_upstream_edges_per_node(x), axis=1
    )
    return nodes


def define_list_upstream_downstream_edges_ids(
    node_ids: np.array,
    nodes: gpd.GeoDataFrame,
    edges: gpd.GeoDataFrame,
    nodes_id_column: str = "nodeID",
    edges_id_column: str = "code",
):
    logging.info("   x find connected edges for nodes")
    nodes_sel = nodes[nodes.nodeID.isin(node_ids)].copy()
    for direction in ["upstream", "downstream"]:
        node_end = "node_end" if direction == "upstream" else "node_start"
        nodes_sel[f"{direction}_edges"] = (
            nodes_sel.merge(
                edges[[node_end, "code"]],
                how="left",
                left_on=nodes_id_column,
                right_on=node_end,
            )
            .groupby(nodes_id_column)
            .agg({edges_id_column: list})
        )
        nodes_sel[f"no_{direction}_edges"] = nodes_sel.apply(
            lambda x: len(x[f"{direction}_edges"]) if x[f"{direction}_edges"] != [np.nan] else 0,
            axis=1,
        )
        nodes_sel[f"{direction}_edges"] = nodes_sel[f"{direction}_edges"].apply(
            lambda x: ",".join(x)
            if ~(type(x[0]) is float and np.isnan(x[0]))
            else ",".join([])
        )
    nodes_sel = nodes_sel.reset_index(drop=True)
    return nodes_sel

