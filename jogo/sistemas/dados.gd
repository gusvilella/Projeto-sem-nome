extends Node
## Carrega os arquivos de dados do jogo (paletas, âncoras, catálogo e regiões).
## Todo conteúdo fica em data/ para poder ser revisado sem mexer em código.

const ARQUIVO_PALETAS := "res://data/personagem/paletas.json"
const ARQUIVO_ANCORAS := "res://data/personagem/ancoras.json"
const ARQUIVO_CATALOGO := "res://data/itens/catalogo.json"
const PASTA_REGIOES := "res://data/regioes/"

var paletas: Dictionary = {}
var ancoras: Dictionary = {}
var base_personagem: Dictionary = {}
var itens: Array = []
var regioes: Dictionary = {}


func _init() -> void:
	paletas = ler_json(ARQUIVO_PALETAS)
	ancoras = ler_json(ARQUIVO_ANCORAS)
	var catalogo := ler_json(ARQUIVO_CATALOGO)
	base_personagem = catalogo.get("base", {})
	itens = catalogo.get("itens", [])
	for arquivo in DirAccess.get_files_at(PASTA_REGIOES):
		if arquivo.ends_with(".json"):
			var regiao := ler_json(PASTA_REGIOES + arquivo)
			regioes[regiao.get("id", arquivo.get_basename())] = regiao


static func ler_json(caminho: String) -> Dictionary:
	var texto := FileAccess.get_file_as_string(caminho)
	var dados = JSON.parse_string(texto)
	if dados is Dictionary:
		return dados
	push_error("Não foi possível ler %s" % caminho)
	return {}


## Lista de paletas de um grupo ("pele", "cabelo" ou "roupa").
func lista_paletas(grupo: String) -> Array:
	return paletas.get(grupo, [])


## Os 8 tons de uma paleta, do contorno à luz.
func cores_da_paleta(grupo: String, indice: int) -> PackedColorArray:
	var lista := lista_paletas(grupo)
	var cores := PackedColorArray()
	if lista.is_empty():
		return cores
	for hex in lista[wrapi(indice, 0, lista.size())]["cores"]:
		cores.append(Color.html(hex))
	return cores


func vetor(par: Array) -> Vector2:
	return Vector2(par[0], par[1])


func item(id: String) -> Dictionary:
	for i in itens:
		if i["id"] == id:
			return i
	return {}


func itens_do_tipo(tipo: String) -> Array:
	return itens.filter(func(i): return i["tipo"] == tipo)
