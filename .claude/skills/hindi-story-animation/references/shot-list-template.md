# Shot list template

```
SCENE <nn> — <Location> — <Day/Night>        BG: <bg symbol/FLA>
Characters: <A (screen L)>, <B (screen R)>     FG: <pot/plant/door>

SH  | Frames      | Type        | Camera                   | Action / Acting                              | Dialogue (speaker)        | Transition in
----|-------------|-------------|--------------------------|----------------------------------------------|---------------------------|--------------
01  | 1–120       | EXT wide    | slow push 100→108%       | A walks L→R to door (walk cycle, 32f)        | —                         | fade-in 15f
02  | 121–210     | INT 2-shot  | hold, drift 2%           | A enters, B stands at R, eyes to A           | —                         | hard cut
03  | 211–420     | MCU B       | push 100→110%            | B talks: mouth 5f loop, sway 13f/50f, point @f260 | "..." (B)            | cut
04  | 421–510     | MCU A       | hold                     | A listens: blink f450, brows worried f470    | —                         | cut
...
```

Dopesheet per shot:
```
SH03  speech: f215–f300, f312–f410   mouth closed: f301–f311
      blinks: f230, f330, f395       gesture: R arm up f255–f262, hold to f290, down f290–f300 (hand=point)
      camera: key f211 scale 100, key f420 scale 110, ease 60
```
