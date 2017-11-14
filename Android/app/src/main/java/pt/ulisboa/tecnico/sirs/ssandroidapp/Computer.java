package pt.ulisboa.tecnico.sirs.ssandroidapp;

import java.io.Serializable;

/**
 * Created by Guilherme on 07/11/2017.
 */

public class Computer implements Serializable {
    private String name = "BANANA"; // bluetooth name FIXME banana
    private String publicKey; // FIXME STRING?

    public void setPublicKey(String publicKey) {
        this.publicKey = publicKey;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() { return name; }
    public String getPublicKey() {
        return publicKey;
    }
}
