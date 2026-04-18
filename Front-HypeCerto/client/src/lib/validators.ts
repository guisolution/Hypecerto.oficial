/**
 * Validadores para o formulário de cadastro
 * Design: Modern Tech Dashboard
 */

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Valida formato de email
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Valida força da senha
 * Requisitos: mínimo 8 caracteres, maiúscula, minúscula, número
 */
export const validatePassword = (password: string): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push("Mínimo de 8 caracteres");
  }
  if (!/[A-Z]/.test(password)) {
    errors.push("Deve conter pelo menos uma letra maiúscula");
  }
  if (!/[a-z]/.test(password)) {
    errors.push("Deve conter pelo menos uma letra minúscula");
  }
  if (!/[0-9]/.test(password)) {
    errors.push("Deve conter pelo menos um número");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Valida se as senhas correspondem
 */
export const validatePasswordMatch = (password: string, confirmPassword: string): boolean => {
  return password === confirmPassword && password.length > 0;
};

/**
 * Valida telefone brasileiro
 * Formato: (11) 99999-9999 ou 11999999999
 */
export const validatePhoneBrazil = (phone: string): boolean => {
  // Remove caracteres especiais
  const cleanPhone = phone.replace(/\D/g, "");
  // Valida se tem 11 dígitos (2 de DDD + 9 dígitos)
  return cleanPhone.length === 11 && /^[1-9]{2}9[0-9]{8}$/.test(cleanPhone);
};

/**
 * Formata telefone brasileiro para exibição
 */
export const formatPhoneBrazil = (phone: string): string => {
  const cleanPhone = phone.replace(/\D/g, "");
  if (cleanPhone.length !== 11) return phone;
  return `(${cleanPhone.slice(0, 2)}) ${cleanPhone.slice(2, 7)}-${cleanPhone.slice(7)}`;
};

/**
 * Valida nome completo (mínimo 1 caractere, sem números)
 * Alterado de 3 para 1 conforme solicitado.
 */
export const validateFullName = (name: string): boolean => {
  return name.trim().length >= 1 && !/[0-9]/.test(name);
};

/**
 * Valida formulário completo de cadastro
 */
export const validateSignupForm = (data: {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  phone?: string;
  acceptTerms: boolean;
}): ValidationError[] => {
  const errors: ValidationError[] = [];

  // Validar nome
  if (!validateFullName(data.fullName)) {
    errors.push({
      field: "fullName",
      message: "Nome completo deve ter pelo menos 1 caracter",
    });
  }

  // Validar email
  if (!validateEmail(data.email)) {
    errors.push({
      field: "email",
      message: "Email inválido. Use o formato: seu@email.com",
    });
  }

  // Validar senha
  const passwordValidation = validatePassword(data.password);
  if (!passwordValidation.valid) {
    errors.push({
      field: "password",
      message: `Senha fraca. ${passwordValidation.errors.join(", ")}`,
    });
  }

  // Validar confirmação de senha
  if (!validatePasswordMatch(data.password, data.confirmPassword)) {
    errors.push({
      field: "confirmPassword",
      message: "As senhas não correspondem",
    });
  }

  // Validar telefone (se fornecido)
  if (data.phone && data.phone.trim() !== "") {
    if (!validatePhoneBrazil(data.phone)) {
      errors.push({
        field: "phone",
        message: "Telefone inválido. Use o formato: (11) 99999-9999",
      });
    }
  }

  // Validar aceite de termos
  if (!data.acceptTerms) {
    errors.push({
      field: "acceptTerms",
      message: "Você deve aceitar os termos de uso e privacidade",
    });
  }

  return errors;
};