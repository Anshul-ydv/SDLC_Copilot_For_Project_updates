import { create } from "zustand";

// ── Types ───────────────────────────────────────────────────────────────
interface UserState {
  userId: string | null;
  email: string | null;
  role: string | null;
  token: string | null;
}

interface DocumentMeta {
  id: string;
  filename: string;
  file_size: number;
  file_type: string;
  upload_date: string;
  status: string;
}

interface AppState {
  // Auth
  user: UserState;
  setUser: (user: UserState) => void;
  clearUser: () => void;

  // Active chat session
  activeSessionId: string | null;
  setActiveSessionId: (id: string | null) => void;

  // Documents
  documents: DocumentMeta[];
  setDocuments: (docs: DocumentMeta[]) => void;
  addDocument: (doc: DocumentMeta) => void;
}

// ── Initial state ───────────────────────────────────────────────────────
const EMPTY_USER: UserState = {
  userId: null,
  email: null,
  role: null,
  token: null,
};

// ── Store ───────────────────────────────────────────────────────────────
export const useAppStore = create<AppState>((set) => ({
  // Auth
  user: EMPTY_USER,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: EMPTY_USER }),

  // Chat
  activeSessionId: null,
  setActiveSessionId: (id) => set({ activeSessionId: id }),

  // Documents
  documents: [],
  setDocuments: (docs) => set({ documents: docs }),
  addDocument: (doc) =>
    set((state) => ({ documents: [doc, ...state.documents] })),
}));
