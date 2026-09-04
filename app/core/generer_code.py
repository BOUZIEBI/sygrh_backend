import secrets
import string



class CodeGenerator:
    @staticmethod
    def generer_code_numerique(n: int) -> str:
        if n <= 0:
            raise ValueError("La longueur doit être supérieure à zéro.")

        return "".join(secrets.choice(string.digits) for _ in range(n))


    @staticmethod
    def generer_code_alphanumerique(n: int) -> str:
        if n <= 0:
            raise ValueError(
                "La longueur doit être supérieure à zéro."
            )

        caracteres = string.ascii_uppercase + string.digits

        return "".join(
            secrets.choice(caracteres)
            for _ in range(n)
        )