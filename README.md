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
+24: "Number (VarInt)"
```

## Brush Types

| Hex.   | Binary     | Type | Number of bytes | Pressure |
| ------ | ---------- | ----------- | --- | ----- |
| `0x00` | `00000000` | Pen         | 46  | True  |
| `0x18` | `00011000` | Pen         | 46  | False |
| `0x02` | `00000010` | Pencil      | 46  | True  |
| `0x1A` | `00011010` | Pencil      | 46  | False |
| `0x05` | `00000101` | Highlighter | 29  | True  |
| `0x1D` | `00011101` | Highlighter | 29  | False |

The three least significant bits determine the type of brush used.

The next two bits indicate whether or not the pressure has been activated.

## Brush Structure

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
---
title: "Brush"
---
packet
+1: "config"
+1: "ff"
+3: "color"
+4: "width"
+4: "height"
+3: "? (if PENCIL)"
+8: "float?"
+8: "float? (if not PENCIL)"
+8: "float? (if not PENCIL)"
+8: "float? (if not PENCIL)"
+8: "float? (if not PENCIL)"
+8: "float? (if not PENCIL)"
```

# Groups

## Number of groups

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%

packet
+24: "Number (VarInt)"
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
+24: "Number (VarInt)"
```

## Figure Structure

```mermaid
%%{init: { "packet": { "bitsPerRow": 24 } }}%%
packet
+3: "id? (VarInt)"
+3: "Brush (VarInt)"
+3: "Group (VarInt)"
+1: "?"
+3: "timestamp? (VarInt)"
+9: "?"
+3: "nb of points (VarInt)"
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
