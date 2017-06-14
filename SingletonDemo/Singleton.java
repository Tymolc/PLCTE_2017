public final class Singleton {
    private static volatile Singleton instance;
    private static String foo;

    private Singleton() {}

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
