"""
Script para visualizar o grafo do workflow.
Gera diagrama Mermaid que pode ser visualizado no navegador.
"""
import sys

# Evitar problemas de encoding
sys.stdout.reconfigure(encoding='utf-8')

from src.graph.workflow import criar_grafo_atendimento

print("Criando grafo...")
grafo = criar_grafo_atendimento()

print("\nGerando diagrama Mermaid...")
mermaid_code = grafo.get_graph().draw_mermaid()

# Salvar em arquivo
with open("workflow_diagram.mmd", "w", encoding="utf-8") as f:
    f.write(mermaid_code)

print("\nDiagrama salvo em: workflow_diagram.mmd")

# Criar HTML para visualizar
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp Bot - Workflow</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        #diagram {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend h3 {{
            margin-top: 0;
        }}
        .legend ul {{
            list-style: none;
            padding: 0;
        }}
        .legend li {{
            padding: 5px 0;
        }}
    </style>
</head>
<body>
    <h1>WhatsApp Bot - Fluxo de Atendimento</h1>

    <div id="diagram">
        <pre class="mermaid">
{mermaid_code}
        </pre>
    </div>

    <div class="legend">
        <h3>Legenda do Fluxo:</h3>
        <ul>
            <li><strong>validar_webhook</strong> - Valida dados do webhook da Evolution API</li>
            <li><strong>verificar_cliente</strong> - Verifica se cliente existe no Supabase</li>
            <li><strong>cadastrar_cliente</strong> - Cadastra novo cliente no banco</li>
            <li><strong>processar_midia</strong> - Roteia para processador específico</li>
            <li><strong>processar_texto</strong> - Processa mensagens de texto</li>
            <li><strong>processar_audio</strong> - Transcreve áudio com Whisper</li>
            <li><strong>processar_imagem</strong> - Analisa imagem com GPT-4 Vision</li>
            <li><strong>processar_agente</strong> - Gera resposta com GPT-4</li>
            <li><strong>fragmentar_resposta</strong> - Divide resposta em fragmentos</li>
            <li><strong>enviar_respostas</strong> - Envia mensagens via WhatsApp</li>
        </ul>
    </div>

    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>"""

with open("workflow_diagram.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Visualização HTML salva em: workflow_diagram.html")
print("\nPara visualizar:")
print("1. Abra o arquivo workflow_diagram.html no navegador")
print("2. Ou acesse: https://mermaid.live e cole o conteúdo de workflow_diagram.mmd")

# Mostrar resumo dos nós
print("\n" + "="*60)
print("RESUMO DO GRAFO")
print("="*60)

nodes = list(grafo.get_graph().nodes.keys())
print(f"\nTotal de nós: {len(nodes)}")
print("\nNós do workflow:")
for i, node in enumerate(nodes, 1):
    print(f"  {i}. {node}")

print("\n" + "="*60)
