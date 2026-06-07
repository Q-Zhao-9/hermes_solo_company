# Class 5 Finance Output Example / 第 5 课财务输出示例

Input:

```text
I paid $29.99 to OpenAI for ChatGPT Plus on June 1, 2026 for my AI consulting business.
```

Expected Finance Agent output:

```json
{
  "date": "2026-06-01",
  "type": "expense",
  "vendor_or_customer": "OpenAI",
  "description": "ChatGPT Plus subscription for AI consulting work",
  "category": "AI Tools",
  "amount": 29.99,
  "currency": "USD",
  "tax_deductible_likely": true,
  "review_needed": false
}
```

Monthly summary should include income, expenses, estimated profit, category totals, cash-flow note, and review warnings.
