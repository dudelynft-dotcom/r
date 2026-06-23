// Build a Merkle tree over a list of addresses (leaf = keccak256(address)).
// Compatible with OpenZeppelin MerkleProof.verify on-chain if you later gate a
// contract by phase. Sorted pairs for deterministic, library-agnostic proofs.
import { MerkleTree } from "merkletreejs";
import keccak256 from "keccak256";

function leafOf(address) {
  // keccak256 of the 20-byte address (lowercased, hex)
  return keccak256(Buffer.from(address.toLowerCase().replace(/^0x/, ""), "hex"));
}

export function buildMerkle(addresses) {
  const unique = [...new Set(addresses.map((a) => a.toLowerCase()))].sort();
  const leaves = unique.map(leafOf);
  const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });
  const root = "0x" + tree.getRoot().toString("hex");
  const proofs = {};
  for (const addr of unique) {
    proofs[addr] = tree.getHexProof(leafOf(addr));
  }
  return { root, count: unique.length, proofs };
}
