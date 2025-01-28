Róznice w czasie, dla tego samego kodu, rozniacego sie wylacznie jedna funkcja
- Euler: 17m 32s
- RK2: 19m 39s
- RK4: 21m 32s

Porównanie Euler i RK4; Czas wykonania wzrósł o około 22,8 %, parametry beta, gamma, mu, R_0 są nieco bardziej "gładkie"
(w eulerze mieliśmy do czynienia z nagłymi zmianami, w RK4 takie sytuacje zdarzają się znacznie rzadziej).
Widać delikatną poprawę w kontekście wyznaczania chociazby "obwiedni" min-max, jednak 
przez to, ze dane same w sobie nie są idealne i moze zdarzyc sie sytuacja, ze w danym dniu nasze dane sa niekompletne(lub bledne),
to ciezko mowic o bezwzglednych bledach ktore otrzymujemy dzieki konkretnym metodom. Jednak wplyw RK4 nie jest tak duzy na model,
by mozna bylo poswiecac dodatkowo 22,8% naszego czasu wykonywania.