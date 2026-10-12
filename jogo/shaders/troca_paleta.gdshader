// Troca de paleta: sprites recoloríveis são desenhados com até 8 tons de cinza
// (28, 56, 84, 112, 140, 168, 196, 224) que viram os 8 tons de uma paleta,
// do contorno à luz. Um único desenho de cabelo vira todas as cores de
// data/personagem/paletas.json.
shader_type canvas_item;

uniform vec4 cores[8];

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	int indice = int(round(c.r * 255.0 / 28.0));
	vec3 cor = c.rgb;
	if (indice >= 1 && indice <= 8) {
		cor = cores[indice - 1].rgb;
	}
	// COLOR.a já traz a transparência da textura multiplicada pelo modulate.
	COLOR = vec4(cor, COLOR.a);
}
