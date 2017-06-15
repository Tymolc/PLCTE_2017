/*
Detected Design Patterns:
Singleton, ref: https://sourcemaking.com/design_patterns/singleton
*/
public final class Singleton {
// Singleton pattern detected here (Instance Field)
    private static volatile Singleton instance;
    private static String foo;

    private Singleton() {}

// Singleton pattern detected here (Accessor Function)
    public static Singleton getInstance(String value) {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

    public static int bar() {
        return 0;
    }
}
