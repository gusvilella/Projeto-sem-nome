extends Node2D
## Cena principal do protótipo da Fase 0: a região Casa do Vale, o personagem
## e o painel de testes.

var vale: Vale
var personagem: Personagem
var camera: Camera2D
var painel: PainelPrototipo


func _ready() -> void:
	vale = Vale.new("casa")
	vale.name = "Vale"
	add_child(vale)

	personagem = Personagem.new()
	personagem.name = "Personagem"
	vale.adicionar_personagem(personagem)

	camera = Camera2D.new()
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 6.0
	var limite := vale.tamanho
	camera.limit_left = 0
	camera.limit_top = 0
	camera.limit_right = limite.x
	camera.limit_bottom = limite.y
	personagem.add_child(camera)

	painel = PainelPrototipo.new()
	add_child(painel)
	painel.configurar(vale, personagem)
