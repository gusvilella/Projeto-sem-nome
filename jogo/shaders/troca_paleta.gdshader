// Troca de paleta: sprites recoloríveis são desenhados com 4 tons de cinza
// (51, 102, 153, 204) que viram contorno, sombra, base e luz.
// Um único desenho de cabelo vira todas as cores de data/personagem/paletas.json.
shader_type canvas_item;

uniform vec4 cor_contorno : source_color = vec4(0.2, 0.2, 0.2, 1.0);
uniform vec4 cor_sombra : source_color = vec4(0.4, 0.4, 0.4, 1.0);
uniform vec4 cor_base : source_color = vec4(0.6, 0.6, 0.6, 1.0);
uniform vec4 cor_luz : source_color = vec4(0.8, 0.8, 0.8, 1.0);

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	int indice = int(round(c.r * 5.0));
	vec3 cor = c.rgb;
	if (indice == 1) {
		cor = cor_contorno.rgb;
	} else if (indice == 2) {
		cor = cor_sombra.rgb;
	} else if (indice == 3) {
		cor = cor_base.rgb;
	} else if (indice == 4) {
		cor = cor_luz.rgb;
	}
	// COLOR.a já traz a transparência da textura multiplicada pelo modulate.
	COLOR = vec4(cor, COLOR.a);
}
