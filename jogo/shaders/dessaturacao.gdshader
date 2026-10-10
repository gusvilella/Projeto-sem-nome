// Mundo desbotado: o cenário é desenhado colorido uma vez só e este shader
// tira a cor de acordo com a vida da região (0 = adormecido, 1 = vivo).
// Ver docs/gdd/05-direcao-de-arte.md#mundo-desbotado.
shader_type canvas_item;

uniform float vida : hint_range(0.0, 1.0) = 0.0;
// Quanto de cor sobra com vida 0. Um pouco de cor evita que o mundo pareça "morto".
uniform float saturacao_minima : hint_range(0.0, 1.0) = 0.2;

void fragment() {
	vec4 c = COLOR;
	float cinza = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	vec3 cor = mix(vec3(cinza), c.rgb, mix(saturacao_minima, 1.0, vida));
	// Leve tom frio e mais escuro enquanto adormecido.
	vec3 frio = cor * vec3(0.88, 0.94, 1.06) * 0.92;
	COLOR = vec4(mix(frio, cor, vida), c.a);
}
