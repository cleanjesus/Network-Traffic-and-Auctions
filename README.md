# Network Traffic and Auctions

CECS 427 (Network Analysis) assignment: apply game theory to network traffic (Braess's paradox) and sealed-bid auctions.

## Features

| Command | What it does |
| --- | --- |
| `traffic` | Reads a directed road network with linear travel-time functions `T(x) = a·x + b` and one shortcut edge. Computes the equilibrium traffic split without the shortcut, then the equilibrium with it, and reports whether Braess's paradox occurs (the shortcut makes everyone slower). |
| `auction` | Reads bidders with a private `value` and a `bid`, then runs a first-price or second-price sealed-bid auction and reports the winner, price paid, and payoff. |

Each command prints its results to stdout and saves a PNG visualization. Invalid input exits with a nonzero status, and there are no interactive prompts.

## Requirements

- Python 3
- [NetworkX](https://networkx.org/)
- [Matplotlib](https://matplotlib.org/)

```bash
pip install networkx matplotlib
```

## Usage

```bash
python3 games.py traffic GRAPH.gml SOURCE TARGET DRIVERS OUTPUT.png
python3 games.py auction GRAPH.gml first|second OUTPUT.png
```

Examples using the included samples:

```bash
python3 games.py traffic samples/traffic.gml S T 4000 traffic.png
python3 games.py auction samples/bidders.gml first first.png
python3 games.py auction samples/bidders.gml second second.png
```

Sample output of `traffic`:

```
NODES 4
EDGES 5
ROUTE_1 S U T
ROUTE_2 S V T
SHORTCUT_ROUTE S U V T
ORIGINAL_FLOW_1 2000.000
ORIGINAL_FLOW_2 2000.000
ORIGINAL_TIME 65.000
SHORTCUT_FLOW 4000.000
SHORTCUT_TIME 80.000
BRAESS_PARADOX YES
```

## Project Structure

| Path | Description |
| --- | --- |
| `games.py` | Main program (`traffic` and `auction` commands) |
| `samples/` | Sample GML inputs (`traffic`, `bidders`) |
| `traffic.png`, `first.png`, `second.png` | Example output images |

## Generative AI Disclosure

Generative AI (Cursor IDE agent) was used to help map lecture material to the required output and plan the program layout. See the header of `games.py` for details.
