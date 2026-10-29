import { describe, it, expect } from "vitest";
import { validateEmail, validatePassword, validatePasswordMatch, validatePhoneBrazil, formatPhoneBrazil, validateFullName, validateSignupForm } from "/tmp/claude-0/ev/fixed/Front-HypeCerto/client/src/lib/validators";

describe("TESTES UNITÁRIOS FRONT — validators.ts", () => {
  it("F01 e-mail válido", () => expect(validateEmail("a@b.com")).toBe(true));
  it("F02 e-mail inválido (sem @, sem domínio, com espaço)", () => { for (const e of ["ab.com","a@b","a b@c.com",""]) expect(validateEmail(e)).toBe(false); });
  it("F03 senha forte aceita", () => expect(validatePassword("Senha123").valid).toBe(true));
  it("F04 senha fraca rejeitada (curta, sem maiúscula, sem número)", () => { expect(validatePassword("abc").valid).toBe(false); expect(validatePassword("senhasenha1").errors).toContain("Deve conter pelo menos uma letra maiúscula"); expect(validatePassword("Senhasenha").errors).toContain("Deve conter pelo menos um número"); });
  it("F05 confirmação de senha", () => { expect(validatePasswordMatch("a","a")).toBe(true); expect(validatePasswordMatch("a","b")).toBe(false); expect(validatePasswordMatch("","")).toBe(false); });
  it("F06 telefone BR válido com e sem máscara", () => { expect(validatePhoneBrazil("(11) 99999-9999")).toBe(true); expect(validatePhoneBrazil("11999999999")).toBe(true); });
  it("F07 telefone BR inválido (fixo, curto, DDD 0x)", () => { expect(validatePhoneBrazil("1133334444")).toBe(false); expect(validatePhoneBrazil("123")).toBe(false); expect(validatePhoneBrazil("01999999999")).toBe(false); });
  it("F08 formatação de telefone", () => expect(formatPhoneBrazil("11999999999")).toBe("(11) 99999-9999"));
  it("F09 nome sem números", () => { expect(validateFullName("Ana Maria")).toBe(true); expect(validateFullName("R2D2")).toBe(false); });
  it("F10 nome de 1 letra é aceito, mas símbolos de marcação são recusados", () => { expect(validateFullName("A")).toBe(true); expect(validateFullName("<script>")).toBe(false); });
  it("F11 mensagem de nome inválido é clara: 'Informe seu nome (sem números).'", () => {
    const errs = validateSignupForm({fullName:"", email:"a@b.com", password:"Senha123", confirmPassword:"Senha123", acceptTerms:true});
    expect(errs[0].message).toBe("Informe seu nome (sem números)."); });
  it("F12 formulário completo válido => 0 erros", () => expect(validateSignupForm({fullName:"Ana", email:"a@b.com", password:"Senha123", confirmPassword:"Senha123", phone:"(11) 99999-9999", acceptTerms:true})).toEqual([]));
  it("F13 formulário inválido acumula erros por campo", () => { const f = validateSignupForm({fullName:"1", email:"x", password:"a", confirmPassword:"b", phone:"1", acceptTerms:false}).map(e=>e.field); expect(f).toEqual(["fullName","email","password","confirmPassword","phone","acceptTerms"]); });
  it("F14 ReDoS: regex de e-mail em entrada longa < 200ms", () => { const t=Date.now(); validateEmail("a".repeat(200000)+"@"); expect(Date.now()-t).toBeLessThan(200); });
});
