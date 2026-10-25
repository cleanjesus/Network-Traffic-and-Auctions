#!/usr/bin/env python3
"""CECS 427 - Network Traffic and Auctions assignment.

Usage:
    python3 games.py traffic GRAPH.gml SOURCE TARGET DRIVERS OUTPUT.png
    python3 games.py auction GRAPH.gml first|second OUTPUT.png

---------------------------------------------------------------------------
Generative AI Disclosure (Syllabus Section 16)
---------------------------------------------------------------------------
The following generative AI tools were used in this assignment:
    Cursor IDE agent (Claude)

Usage of AI:
    - Used AI to map the lecture slides (Modeling Network Traffic Using
      Game Theory, Auctions) to the required output fields and plan the
      program layout.
---------------------------------------------------------------------------
"""

import os
import sys

import matplotlib.pyplot as plt
import networkx as nx

plt.switch_backend("Agg")


def fail(message):
    """Print an error to stderr and exit with a nonzero status."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_graph(path):
    if not os.path.isfile(path):
        fail(f"file not found: {path}")
    try:
        return nx.read_gml(path)
    except Exception as exc:
        fail(f"could not read GML file {path}: {exc}")


def fmt3(x):
    return f"{x:.3f}"


def finish(lines, fig, output):
    """Save the PNG, then print the result lines and GRAPH_IMAGE."""
    fig.savefig(output, format="png", bbox_inches="tight")
    plt.close(fig)
    for line in lines:
        print(line)
    print(f"GRAPH_IMAGE {output}")


def path_edges(path):
    return list(zip(path, path[1:]))


def cmd_traffic(args):
    path, source, target, drivers, output = args
    try:
        D = float(drivers)
    except ValueError:
        fail(f"DRIVERS must be a number: {drivers}")
    if D <= 0:
        fail("DRIVERS must be positive")

    G = load_graph(path)
    if not G.is_directed():
        fail("traffic graph must be directed")
    if source not in G or target not in G or source == target:
        fail("invalid source or target")
    for u, v, data in G.edges(data=True):
        if "a" not in data or "b" not in data:
            fail(f"edge {u}->{v} is missing a or b")

    shortcuts = [(u, v) for u, v, d in G.edges(data=True) if d.get("shortcut") == 1]
    if len(shortcuts) != 1:
        fail("traffic graph must have exactly one shortcut edge")
    shortcut = shortcuts[0]

    def coeffs(route):
        edges = path_edges(route)
        return (sum(G.edges[e]["a"] for e in edges),
                sum(G.edges[e]["b"] for e in edges))

    # Original network (Traffic Slides 2-7): remove the shortcut, equalize route times.
    H = G.copy()
    H.remove_edge(*shortcut)
    routes = sorted(nx.all_simple_paths(H, source, target))
    if len(routes) != 2:
        fail("graph must have exactly two routes without the shortcut")
    route1, route2 = routes
    A1, B1 = coeffs(route1)
    A2, B2 = coeffs(route2)
    if A1 + A2 == 0:
        fail("routes have no congestible edges; equilibrium is undefined")
    x = (A2 * D + B2 - B1) / (A1 + A2)
    original_time = A1 * x + B1

    # With the shortcut (Traffic Slides 8-10): all D drivers take the shortcut route.
    shortcut_routes = sorted(
        r for r in nx.all_simple_paths(G, source, target)
        if shortcut in path_edges(r)
    )
    if not shortcut_routes:
        fail("no source-to-target route uses the shortcut")
    shortcut_route = shortcut_routes[0]
    A, B = coeffs(shortcut_route)
    shortcut_time = A * D + B
    paradox = "YES" if shortcut_time > original_time else "NO"

    lines = [
        f"NODES {G.number_of_nodes()}",
        f"EDGES {G.number_of_edges()}",
        " ".join(["ROUTE_1"] + route1),
        " ".join(["ROUTE_2"] + route2),
        " ".join(["SHORTCUT_ROUTE"] + shortcut_route),
        f"ORIGINAL_FLOW_1 {fmt3(x)}",
        f"ORIGINAL_FLOW_2 {fmt3(D - x)}",
        f"ORIGINAL_TIME {fmt3(original_time)}",
        f"SHORTCUT_FLOW {fmt3(D)}",
        f"SHORTCUT_TIME {fmt3(shortcut_time)}",
        f"BRAESS_PARADOX {paradox}",
    ]

    pos = {source: (0, 0), target: (2, 0)}
    for route, y in ((route1, 1), (route2, -1)):
        inner = route[1:-1]
        for i, n in enumerate(inner, start=1):
            pos[n] = (2 * i / (len(inner) + 1), y)
    for n in G:
        pos.setdefault(n, (1, 0))

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.axis("off")
    original_edges = [e for e in G.edges() if e != shortcut]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color="lightblue", node_size=1200)
    nx.draw_networkx_labels(G, pos, ax=ax)
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=original_edges, edge_color="gray",
        style="solid", width=2, arrowsize=20, node_size=1200,
    )
    nx.draw_networkx_edges(
        G, pos, ax=ax, edgelist=[shortcut], edge_color="red",
        style="dashed", width=2, arrowsize=20, node_size=1200,
    )
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax,
        edge_labels={(u, v): f"T(x)={d['a']:g}x+{d['b']:g}"
                     for u, v, d in G.edges(data=True)},
    )
    ax.set_title(
        f"Braess Network: original time {fmt3(original_time)}, "
        f"shortcut time {fmt3(shortcut_time)}"
    )

    finish(lines, fig, output)


def cmd_auction(args):
    path, kind, output = args
    if kind not in ("first", "second"):
        fail("auction type must be first or second")

    G = load_graph(path)
    if G.number_of_nodes() < 2:
        fail("auction needs at least two bidders")
    for n, data in G.nodes(data=True):
        if "value" not in data or "bid" not in data:
            fail(f"bidder {n} is missing value or bid")

    bid = {n: float(d["bid"]) for n, d in G.nodes(data=True)}
    ranked = sorted(G.nodes(), key=lambda n: (-bid[n], str(n)))
    winner = ranked[0]
    # First price (Auctions Slide 6): pay own bid. Second price (Slide 7): pay second-highest bid.
    price = bid[winner] if kind == "first" else bid[ranked[1]]
    value = float(G.nodes[winner]["value"])

    lines = [
        f"BIDDERS {G.number_of_nodes()}",
        f"TYPE {kind.upper()}",
        f"WINNER {winner}",
        f"WINNING_BID {fmt3(bid[winner])}",
        f"PRICE {fmt3(price)}",
        f"WINNER_VALUE {fmt3(value)}",
        f"WINNER_PAYOFF {fmt3(value - price)}",
    ]

    pos = nx.circular_layout(sorted(G.nodes()))
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.axis("off")
    nx.draw_networkx_nodes(
        G, pos, ax=ax, node_size=3000,
        node_color=["green" if n == winner else "lightblue" for n in G.nodes()],
    )
    nx.draw_networkx_labels(
        G, pos, ax=ax, font_size=9,
        labels={n: f"{n}\nvalue={float(d['value']):g}\nbid={bid[n]:g}"
                for n, d in G.nodes(data=True)},
    )
    ax.set_title(
        f"{kind.capitalize()}-Price Sealed-Bid Auction: "
        f"winner {winner}, price {fmt3(price)}"
    )
    ax.margins(0.2)

    finish(lines, fig, output)


COMMANDS = {
    "traffic": (5, cmd_traffic, "GRAPH.gml SOURCE TARGET DRIVERS OUTPUT.png"),
    "auction": (3, cmd_auction, "GRAPH.gml first|second OUTPUT.png"),
}


def main():
    if len(sys.argv) < 2:
        fail("usage: games.py traffic|auction ...")

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in COMMANDS:
        fail(f"unknown command: {command}")

    expected, handler, usage = COMMANDS[command]
    if len(args) != expected:
        fail(f"usage: games.py {command} {usage}")

    handler(args)


if __name__ == "__main__":
    main()
