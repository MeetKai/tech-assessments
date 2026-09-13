import { afterEach, expect, test, vi } from 'vitest';
import { api } from './api';

afterEach(() => vi.unstubAllGlobals());
test('preserva o código de atendimento retornado pelo serviço', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({message: 'Documento não encontrado.', request_id: 'atendimento-1'}), {status: 404})));
  await expect(api('/documents/999')).rejects.toMatchObject({status: 404, requestId: 'atendimento-1'});
});
