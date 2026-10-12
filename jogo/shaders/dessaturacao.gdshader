// Mundo desbotado: a cena é desenhada colorida uma vez só e este shader tira a
// cor de acordo com a vida da região (0 = adormecida, 1 = viva). Perto de 100%
// a luz esquenta para o dourado de fim de tarde.
// Ver docs/gdd/05-direcao-de-arte.md#mundo-desbotado-e-luz.
shader_type canvas_item;

uniform float vida : hint_range(0.0, 1.0) = 0.0;
// Quanto de cor sobra com vida 0. Um pouco de cor evita que o mundo pareça "morto".
uniform float saturacao_minima : hint_range(0.0, 1.0) = 0.2;

void fragment() {
	vec4 c = COLOR;
	float cinza = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	vec3 cor = mix(vec3(cinza), c.rgb, mix(saturacao_minima, 1.0, vida));
	// Adormecida: tom frio e um pouco mais escuro.
	vec3 frio = cor * vec3(0.88, 0.94, 1.06) * 0.92;
	// Viva: luz quente de fim de tarde.
	vec3 quente = cor * vec3(1.07, 1.0, 0.86) + vec3(0.03, 0.018, 0.0);
	vec3 base = mix(frio, cor, smoothstep(0.0, 0.7, vida));
	COLOR = vec4(mix(base, quente, smoothstep(0.7, 1.0, vida) * 0.75), c.a);
}
