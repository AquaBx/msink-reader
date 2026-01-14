# Header

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+18: "Header"
```

# Brushes

## Number of brushes

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+24: "Number (Variable Integer)"
```

## Brush Structure #1

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
---
title: "Brush"
---
packet
+1: "1d"
+1: "ff"
+3: "color"
+4: "width"
+4: "height"
+11: "?"
+5: "?"
```

## Brush Structure #2

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
---
title: "Brush 2"
---
packet
+1: "00/18"
+1: "ff"
+3: "color"
+4: "width"
+4: "height"
+11: "?"

+2: "803f"
+2: "0000"
+2: "0000"
+2: "0000"
+2: "0000"
+2: "0000"

+2: "803f"
+2: "0000"
+2: "0000"
+2: "0000"
+2: "0000"
```

# Groups

## Number of groups

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%

packet
+24: "Number (Variable Integer)"
```

## Group Structure

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%

packet
+2: "803f"
+2: "0000"
+2: "0000"
+2: "?"
+2: "offset x"
+2: "offset y"
```

# Figure

## Number of figures

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+24: "Number (Variable Integer)"
```

## Figure Structure

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+6: "id? (Variable Integer)"
+1: "Brush"
+1: "Group"
+1: "?"
+6: "timestamp? (Variable Integer)"
+9: "?"
+24: "nb of points (Variable Integer)"
```

## Point Structure

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+4: "x"
+4: "y"
+4: "pressure"
+16: "?"
```
