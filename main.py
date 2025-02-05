class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        # DFA'yı tanımlamak için kullanılan yapıcı (constructor) fonksiyon.
        # states: DFA'nın durumlarının kümesi.
        # alphabet: DFA'nın kullandığı giriş alfabesi.
        # transitions: DFA'nın geçiş fonksiyonu (bir sözlük olarak tanımlanmış).
        # start_state: Başlangıç durumu.
        # accept_states: Kabul durumlarının kümesi.
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states
        self.state_mapping = {}  # Minimizasyon sırasında birleştirilen durumları saklamak için kullanılır.

    def remove_unreachable_states(self):
        # Ulaşılamayan durumları kaldırmak için kullanılan fonksiyon.
        reachable = set()  # Ulaşılabilir durumları tutmak için bir küme.
        queue = [self.start_state]  # Başlangıç durumu ile başlıyoruz.

        while queue:
            # Breadth-First Search (BFS) algoritmasıyla tüm ulaşılabilir durumları buluyoruz.
            state = queue.pop(0)
            if state not in reachable:
                reachable.add(state)  # Ulaşılan durumu kümesine ekle.
                for symbol in self.alphabet:
                    # Şu anki durumdan belirli bir giriş sembolüyle gidilen durumu kontrol et.
                    next_state = self.transitions.get(state, {}).get(symbol)
                    if next_state and next_state not in reachable:
                        queue.append(next_state)

        # Ulaşılamayan durumları sözlüklerden ve listelerden kaldır.
        self.states = reachable
        self.transitions = {state: trans for state, trans in self.transitions.items() if state in reachable}
        self.accept_states = [state for state in self.accept_states if state in reachable]

    def minimize(self):
        # DFA minimizasyon işlemi (denk durumları birleştirme).

        # İlk adım: Kabul ve kabul olmayan durumları iki ayrı gruba ayır.
        partitions = [set(self.accept_states), set(self.states) - set(self.accept_states)]

        while True:
            # Partition'ları tekrar tekrar bölerek minimize ediyoruz.
            new_partitions = []
            for group in partitions:
                grouped = {}
                for state in group:
                    # Her durum için, geçiş yaptığı durumların hangi partition'a düştüğünü kontrol et.
                    key = tuple(
                        (
                        symbol, frozenset(self.find_partition(self.transitions.get(state, {}).get(symbol), partitions)))
                        for symbol in self.alphabet
                    )
                    grouped.setdefault(key, set()).add(state)  # Aynı davranış sergileyen durumları grupla.
                new_partitions.extend(grouped.values())  # Yeni partition'ları oluştur.
            if new_partitions == partitions:
                # Yeni partition'lar eskisiyle aynıysa işlem tamamdır.
                break
            partitions = new_partitions

        # İkinci adım: Yeni DFA oluştur.
        # Yeni durumlar için bir sözlük oluştur, her partition bir yeni durumu temsil eder.
        new_states = {frozenset(part): f"q{idx}" for idx, part in enumerate(partitions)}
        new_transitions = {}
        new_accept_states = set()

        # Birleştirilmiş durumları takip etmek için mapping oluştur.
        self.state_mapping = {new_states[frozenset(part)]: part for part in partitions}

        for part in partitions:
            # Her partition için, temsilci bir durumu seç ve onun üzerinden geçişleri belirle.
            representative = next(iter(part))
            new_state = new_states[frozenset(part)]
            if representative in self.accept_states:
                new_accept_states.add(new_state)  # Eğer temsilci kabul durumuysa, yeni durum da kabul durumu olur.

            new_transitions[new_state] = {}
            for symbol in self.alphabet:
                next_state = self.transitions.get(representative, {}).get(symbol)
                if next_state:
                    # Temsilcinin geçiş yaptığı durumu bul ve onun hangi partition'da olduğunu kontrol et.
                    next_partition = self.find_partition(next_state, partitions)
                    new_transitions[new_state][symbol] = new_states[frozenset(next_partition)]

        # Yeni durumlar, geçişler, kabul durumları ve başlangıç durumu ile DFA'yı güncelle.
        self.states = set(new_states.values())
        self.transitions = new_transitions
        self.accept_states = new_accept_states
        self.start_state = new_states[frozenset(self.find_partition(self.start_state, partitions))]

    @staticmethod
    def find_partition(state, partitions):
        # Belirtilen bir durumun hangi partition'a ait olduğunu bulan yardımcı fonksiyon.
        for part in partitions:
            if state in part:
                return frozenset(part)
        return None

    def display(self):
        # DFA'nın bilgilerini yazdıran fonksiyon.
        print("States:", self.states)
        print("Alphabet:", self.alphabet)
        print("Start State:", self.start_state)
        print("Accept States:", self.accept_states)
        print("Transitions:")
        for state, trans in self.transitions.items():
            print(f"  {state}: {trans}")
        print("\nMerged States Mapping:")
        for new_state, original_states in self.state_mapping.items():
            # Birleştirilen durumları ve bunların hangi yeni duruma karşılık geldiğini yazdır.
            print(f"  {new_state} -> {original_states}")


# Örnek DFA tanımı
states = {"q0", "q1", "q2", "q3", "q4", "q5", "q6"}  # Durumlar
alphabet = {"0", "1"}  # Giriş alfabesi
transitions = {
    "q0": {"0": "q1", "1": "q2"},
    "q1": {"0": "q3", "1": "q4"},
    "q2": {"0": "q5", "1": "q6"},
    "q3": {"0": "q3", "1": "q4"},
    "q4": {"0": "q5", "1": "q6"},
    "q5": {"0": "q3", "1": "q4"},
    "q6": {"0": "q5", "1": "q6"}
}  # Geçiş fonksiyonu
start_state = "q0"  # Başlangıç durumu
accept_states = {"q5"}  # Kabul durumları

# DFA nesnesi oluşturuluyor.
dfa = DFA(states, alphabet, transitions, start_state, accept_states)
print("Orijinal DFA:")
dfa.display()

# Ulaşılamayan durumların kaldırılması
dfa.remove_unreachable_states()
print("\nUlaşılamayan durumlar kaldırıldı:")
dfa.display()

# Durumların minimize edilmesi
dfa.minimize()
print("\nMinimize edilmiş DFA:")
dfa.display()
