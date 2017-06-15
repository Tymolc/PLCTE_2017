interface Element {
    void accept(Visitor v);
}

interface Test {
    void accept(Visitor v);
}

class FOO implements Element {
    public void accept(Visitor v) {
        v.visit(this);
    }

    public String getFOO() {
        return "FOO";
    }
}

class BAR implements Element {
    public void accept( Visitor v ) {
        v.visit( this );
    }

    public String getBAR() {
        return "BAR";
    }
}

class BAZ implements Element {
    public void accept(Visitor v) {
        v.visit(this);
    }

    public String getBAZ() {
        return "BAZ";
    }
}

class TestTest implements Test {
    public String getBAZ() {
        return "BAZ";
    }
}

interface Visitor {
    void visit(FOO foo);
    void visit(BAR bar);
    void visit(BAZ baz);
}

class UpVisitor implements Visitor {
    private static volatile UpVisitor instance;

    private UpVisitor() {}

    public static UpVisitor getInstance(String value) {
        if (instance == null) {
            synchronized (UpVisitor.class) {
                if (instance == null) {
                    instance = new UpVisitor();
                }
            }
        }
        return instance;
    }

    public void visit(FOO foo) {
        System.out.println("do Up on " + foo.getFOO());
    }

    public void visit(BAR bar) {
        System.out.println("do Up on " + bar.getBAR());
    }

    public void visit(BAZ baz) {
        System.out.println( "do Up on " + baz.getBAZ() );
    }

    public void visit(TestTest test) {
        System.out.println( "no visitor");
    }
}

class DownVisitor implements Visitor {
    public void visit(FOO foo) {
        System.out.println("do Down on " + foo.getFOO());
    }

    public void visit(BAR bar) {
        System.out.println("do Down on " + bar.getBAR());
    }

    public void visit(BAZ baz ) {
        System.out.println("do Down on " + baz.getBAZ());
    }

    public void visit(TestTest baz ) {
        System.out.println("do Down on " + baz);
    }
}

public class VisitorDemo {
    public static void main( String[] args ) {
        Element[] list = {new FOO(), new BAR(), new BAZ()};
        UpVisitor up = new UpVisitor();
        DownVisitor down = new DownVisitor();
        for (Element element : list) {
            element.accept(up);
        }
        for (Element element : list) {
            element.accept(down);
        }
    }
}
