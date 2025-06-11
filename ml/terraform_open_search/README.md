
# 📘 README.md – Implantação do Amazon OpenSearch com Terraform

## 📁 Estrutura do projeto
```
compliance_ia/
├── ml/
│   └── terraform/
│       ├── main_opensearch.tf
│       ├── variables.tf (se aplicável)
│       ├── outputs.tf   (opcional)
│       └── README.md    ← (este arquivo)
```

---
 


## 🚀 Passo a passo para criar o OpenSearch

### 1. Inicializar o Terraform
```bash
terraform init
```

### 2. Validar a configuração
```bash
terraform validate
```

### 3. Visualizar o que será criado
```bash
terraform plan
```

### 4. Aplicar a infraestrutura
```bash
terraform apply
```

> ⚠️ **Importante:** Aguarde até que a criação do domínio seja finalizada. Isso pode levar **5 a 10 minutos**.

---

## 🔎 Como verificar o domínio

Acesse o Console AWS:
- https://console.aws.amazon.com/opensearch/
- Verifique o domínio `compliance-opensearch`

---

## 💵 Custo estimado

Com a configuração atual (`r5.large.search`, 10 GiB, gp2), o custo é **aproximadamente $40–$50/mês**, dependendo da região e tempo de uso.

---

## 🧹 Como destruir a infraestrutura

Se você estiver apenas testando e quiser evitar cobrança:

```bash
terraform destroy
```

> ⚠️ **Confirme com `yes`** para excluir todos os recursos criados.

---

## 🧠 Dicas importantes

- **Evite encerrar o apply com `Ctrl+C`**.
- Use apenas 1 zona de disponibilidade (`1-AZ`) se estiver otimizando custos.
- Use `gp2` com volume pequeno para testes (mínimo de 10 GiB).
- Você pode alterar o nome do arquivo para `main_opensearch.tf`, sem problemas.
