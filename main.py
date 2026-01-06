import argparse
import logging
import sys
import os

#profiling.py
try:
    from profiling import measure_performance
except ImportError:
    #an leeipei to profiling.py, trekse to sketo
    def measure_performance(func): return func

logging.basicConfig(#emfanizontai INFO, WARNING, ERROR, CRITICAL
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',#Wra, hmeromhnia, info, error, mhnyma pou grafoume emeis sto log
    handlers=[logging.StreamHandler(sys.stdout)]#Steile ta logs sthn othonh, sys.stdout na pane stohn konsola
)


def main():
    parser = argparse.ArgumentParser(description="Neuro-Symbolic HEV Control System CLI")#emfanizetai an pathsoume python main.py --help
    
    # Modes
    parser.add_argument(
        '--mode',#kaleitai me python main.py --mode train 
        type=str, 
        choices=['train', 'evaluate', 'demo', 'ablation', 'optimize'],#mono afta mporei na grapsei o xrhsths alliws varaei error
        required=True,#an den dwseis mode den trexei to programma
        help='Select operation mode'
    )

    # Parameters
    parser.add_argument('--steps', type=int, default=100000, help='Training steps')#posa timesteps tha ekpaideftei o PPO Agent,an den dwseis int tha exoume 100000
    parser.add_argument('--lr', type=float, default=0.0003, help='Learning rate')
    parser.add_argument('--traffic', type=str, default='normal', choices=['low', 'normal', 'heavy'])# px mporoume an to kalesoume me python main.py --mode train --traffic heavy
    parser.add_argument('--driver_mood', type=str, default='neutral', help='Prompt for Demo')
    
    parser.add_argument('--model_path', type=str, default='models/ppo_hev', help='Model file path')#edw leei pou tha apothikefsoume to arxeio

    args = parser.parse_args()#afto diavazei ola ta arguments pou edwse o xrhsths sth consola

    logging.info(f"Starting System in [{args.mode.upper()}] mode")#ta kanoume k kefalaia na einai efdiakrita
    
    #ektelesh me profiling
    try:
        from AI_agent import train_ppo             # Train Mode
        from full_system import run_live_system    # Demo Mode
        from evaluate_agent import run_evaluation  # Evaluate Mode
        from optimize import run_grid_search       # Optimize Mode
        from run_ablation import run_study         # Ablation Mode

        if args.mode == 'train':
            logging.info("Starting PPO Training...")
            measured_train = measure_performance(train_ppo)
            measured_train(steps=args.steps, lr=args.lr, save_path=args.model_path, traffic=args.traffic)
            logging.info("Training Done.")

        elif args.mode == 'evaluate':#gia na doume oti doulevei swsta
            logging.info("Running Evaluation...")
            measured_eval = measure_performance(run_evaluation)
            measured_eval(model_path=args.model_path, traffic=args.traffic)

        elif args.mode == 'demo':#trexei to full_system.py
            logging.info("Initializing Live Demo...")
            measured_demo = measure_performance(run_live_system)
            measured_demo(prompt=args.driver_mood, model_path=args.model_path)
            
        elif args.mode == 'optimize':
            logging.info("Starting Grid Search...")
            measured_opt = measure_performance(run_grid_search)
            measured_opt()

        elif args.mode == 'ablation':
            logging.info("Running Ablation Study...")
            measured_ablation = measure_performance(run_study)
            measured_ablation()
    
    except ImportError as e:#energopoieitai mono an exoume thema me ta imports
        logging.error(f"Could not import module: {e}")
        logging.error("Tip: Get assured that your files (train_agent.py etc.) are in the same folder.")  

    except Exception as e:
        logging.error(f"Critical Error during execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()