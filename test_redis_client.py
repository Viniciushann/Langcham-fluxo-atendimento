"""
Teste simples do RedisClient para verificar se não há erros.
"""

import asyncio
from src.clients.redis_client import RedisQueue, criar_redis_queue

async def test_redis_client():
    """Testa imports e estrutura do RedisQueue."""
    print("Testando RedisClient...")
    print()

    # 1. Verificar que a classe existe
    print("1. Verificando classe RedisQueue...")
    assert RedisQueue is not None
    print("   [OK] Classe RedisQueue existe")

    # 2. Verificar métodos principais
    print("\n2. Verificando métodos da classe...")
    metodos_esperados = [
        'adicionar_mensagem',
        'buscar_mensagens',
        'limpar_fila',
        'contar_mensagens',
        'obter_primeira_mensagem',
        'remover_primeira_mensagem',
        'fila_existe',
        'definir_ttl',
        'close'
    ]

    for metodo in metodos_esperados:
        assert hasattr(RedisQueue, metodo), f"Método {metodo} não encontrado"
        print(f"   [OK] Método {metodo} existe")

    # 3. Verificar factory function
    print("\n3. Verificando factory function...")
    assert criar_redis_queue is not None
    print("   [OK] Factory function criar_redis_queue existe")

    print("\n[OK] Todos os testes passaram!")
    print("[OK] RedisClient nao tem erros de estrutura/import")
    print()
    print("NOTA: Para testar funcionalidade completa, é necessário:")
    print("  - Servidor Redis rodando em localhost:6379")
    print("  - Executar os testes de integração")

if __name__ == '__main__':
    asyncio.run(test_redis_client())
