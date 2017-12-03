package pt.ulisboa.tecnico.sirs.ssandroidapp;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.io.ObjectInputStream;

public class MainActivity extends AppCompatActivity {
    Computer computer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        TextView tv = findViewById(R.id.deviceNameTV);

        if (getComputer()) {
            tv.setText(computer.getName());
            Button b = findViewById(R.id.connectionButton);
            b.setVisibility(View.VISIBLE);
            b = findViewById(R.id.unpairButton);
            b.setVisibility(View.VISIBLE);

            if (getIntent().getStringExtra(Constants.PASSWORD_ID) != null)  // if unpair was called
                unpair();
        }
        else tv.setText(R.string.no_current_computer);
    }

    public void changeActivity2BluetoothPair(View view) {
        if (computer != null) { // if android is already paired, ask user the computer password before making a new pair
            Intent intent = new Intent(this, PasswordVerifyActivity.class);
            String nextClassName = PasswordRequestActivity.class.getName();
            intent.putExtra(Constants.NEXT_CLASS_ID, nextClassName);
            intent.putExtra(Constants.COMPUTER_OBJ, computer);
            startActivity(intent);
            return;
        }
        Intent intent = new Intent(this, PasswordRequestActivity.class);
        startActivity(intent);
    }

    public boolean getComputer() {
        boolean success = false;
        try {
            ObjectInputStream ois = new ObjectInputStream(this.openFileInput(Constants.COMPUTER_OBJ_FILENAME));
            computer = (Computer) ois.readObject();
            ois.close();
            if (computer != null)
                success = true;
        } catch (IOException ie) {
            // pairing not done yet or filesystem error -> pairing phase needs to be done again
            Toast.makeText(getApplicationContext(), R.string.IOException_read_obj_error_msg, Toast.LENGTH_LONG).show();
        } catch (ClassNotFoundException ce) {
            // unable to get computer obj, pairing needs to be done again
            Toast.makeText(getApplicationContext(), R.string.ClassNotFoundException_error_msg, Toast.LENGTH_LONG).show();
        }

        return success;
    }

    public void changeActivity2Connection(View view){
        Intent intent = new Intent(this, PasswordVerifyActivity.class);
        String nextClassName = ConnectionActivity.class.getName();
        intent.putExtra(Constants.NEXT_CLASS_ID, nextClassName);
        intent.putExtra(Constants.COMPUTER_OBJ, computer);
        startActivity(intent);
    }

    public void unpair(View view) {
        Intent intent = new Intent(this, PasswordVerifyActivity.class); // asks user the computer password if you want to unpair
        String nextClassName = MainActivity.class.getName(); // next activity after password verify is a main with a password on the intent
        intent.putExtra(Constants.NEXT_CLASS_ID, nextClassName);
        startActivity(intent);
    }

    private void unpair() {
        this.deleteFile(Constants.COMPUTER_OBJ_FILENAME);

        // hides ui related to computer
        Button b = findViewById(R.id.connectionButton);
        b.setVisibility(View.INVISIBLE);
        b = findViewById(R.id.unpairButton);
        b.setVisibility(View.INVISIBLE);

        TextView tv = findViewById(R.id.deviceNameTV);
        tv.setText(R.string.no_current_computer);
        computer = null;
    }

}
