"""Basic correctness checks for ML-KEM parameter sets."""

from __future__ import annotations

import oqs


ALGORITHMS = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]


def main() -> None:
    for algorithm in ALGORITHMS:
        print(f"\nTesting {algorithm}")
        with oqs.KeyEncapsulation(algorithm) as kem:
            public_key = kem.generate_keypair()
            ciphertext, shared_secret_enc = kem.encap_secret(public_key)
            shared_secret_dec = kem.decap_secret(ciphertext)

            print("public key length:", len(public_key))
            print("secret key length:", kem.details["length_secret_key"])
            print("ciphertext length:", len(ciphertext))
            print("shared secret length:", len(shared_secret_enc))
            print("shared secrets match:", shared_secret_enc == shared_secret_dec)


if __name__ == "__main__":
    main()
